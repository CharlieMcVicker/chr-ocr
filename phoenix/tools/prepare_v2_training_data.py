#!/usr/bin/env python3
"""
Migrates manifest_w_lang.json to preserve labeled/nasty_crop v1 entries, 
and extracts newly improved v2 crops (using skew correction, dynamic margins,
and projection splitting) for all scans.
"""
import os
import sys
import json
import argparse
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phoenix.layout.segmentation import extract_columns, crop_pad_normalize_line, split_merged_crop_by_projection, find_best_block
from server.process_file import ocr_image_to_text
from phoenix.layout.classification import analyze_text
from surya.detection import DetectionPredictor

def find_scans(base_dir):
    supported = (".jp2", ".png", ".jpg", ".jpeg", ".tiff", ".bmp")
    scan_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.startswith("bbox_overlay_"):
                continue
            if f.lower().endswith(supported):
                scan_files.append(os.path.relpath(os.path.join(root, f), base_dir))
    return sorted(scan_files)

def main():
    parser = argparse.ArgumentParser(description="Create v2 manifest with preserved v1 labels and new v2 line crops.")
    parser.add_argument("--input-dir", default="scans", help="Directory containing raw page scans")
    parser.add_argument("--output-dir", default="training_data", help="Output directory")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of new scans to process (0 = all)")
    args = parser.parse_args()

    input_manifest_path = os.path.join(args.output_dir, "manifest_w_lang.json")
    output_manifest_path = os.path.join(args.output_dir, "manifest.json")
    
    # 1. Load and Migrate current manifest to preserve labeled/verified v1 entries
    v1_count = 0
    new_manifest = {}
    
    # Try loading existing manual labels from manifest_w_lang.json first, fallback to manifest.json
    source_path = input_manifest_path if os.path.exists(input_manifest_path) else output_manifest_path
    
    if os.path.exists(source_path):
        with open(source_path, "r", encoding="utf-8") as f:
            old_manifest = json.load(f)
        
        for k, v in old_manifest.items():
            # Keep only manually labeled/verified or nasty crops
            if v.get("status") in ["labeled", "nasty_crop"]:
                v["crop_version"] = "v1"
                new_manifest[k] = v
                v1_count += 1
        print(f"Preserved {v1_count} labeled/verified v1 line crops from {source_path}.")
    else:
        print("No existing manifest found. Starting fresh.")

    # Find raw scans
    scans = find_scans(args.input_dir)
    print(f"Found {len(scans)} raw page scans in '{args.input_dir}'.")

    # 2. Track completed scans for v2 to allow restartability
    completed_scans_path = os.path.join(args.output_dir, "v2_completed_scans.json")
    v2_completed = set()
    if os.path.exists(completed_scans_path):
        with open(completed_scans_path, "r", encoding="utf-8") as f:
            v2_completed = set(json.load(f))
        print(f"Loaded {len(v2_completed)} completed v2 scans.")

    scans_to_process = [s for s in scans if s not in v2_completed]
    if args.limit > 0:
        scans_to_process = scans_to_process[:args.limit]

    if not scans_to_process:
        print("No new scans to process for v2 line crops.")
        # Save manifest with only preserved v1 entries
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(new_manifest, f, indent=2, ensure_ascii=False)
        sys.exit(0)

    # Initialize layout models
    print("Initializing Surya models...")
    from server.layout import get_layout_predictor
    layout_predictor = get_layout_predictor()
    line_detector = DetectionPredictor()

    crops_dir = os.path.join(args.output_dir, "line_crops")
    os.makedirs(crops_dir, exist_ok=True)

    print(f"Processing {len(scans_to_process)} scans for v2 line crops...")
    
    for idx, rel_path in enumerate(scans_to_process, 1):
        scan_path = os.path.join(args.input_dir, rel_path)
        print(f"[{idx}/{len(scans_to_process)}] Processing: {rel_path}")
        
        path_parts = rel_path.replace(os.sep, "_")
        prefix = os.path.splitext(path_parts)[0]

        try:
            # Phase 1: Global Pre-Straightening Skew Correction is handled inside extract_columns
            pil_img = Image.open(scan_path).convert("RGB")
        except Exception as e:
            print(f"  Failed to open image: {e}")
            continue

        try:
            # Dynamic Column margins are handled inside extract_columns
            columns = extract_columns(pil_img)
        except Exception as e:
            print(f"  Layout column extraction failed: {e}")
            continue

        v2_lines_extracted = 0

        for col_idx, col in enumerate(columns):
            c_xmin, c_ymin, _, _ = col["bbox"]
            col_crop = col["image"]

            # Classify column language content via OCR
            try:
                col_ocr = ocr_image_to_text(col_crop, lang="chr+eng")
                classification = analyze_text(col_ocr)
                lang_class = classification["classification"]
            except Exception as e:
                print(f"    OCR Classification failed for Column {col_idx:02d}: {e}")
                continue

            if lang_class in ["Cherokee", "Mixed"]:
                # Segment lines in column crop
                try:
                    predictions = line_detector([col_crop])
                    pred = predictions[0]
                    detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
                except Exception as e:
                    print(f"      Line detection failed for Column {col_idx:02d}: {e}")
                    continue

                for line_idx, line_obj in enumerate(detected_lines):
                    lx1, ly1, lx2, ly2 = line_obj.bbox
                    unpadded_height = max(1, int(ly2) - int(ly1))
                    target_height = 30

                    sub_bboxes = []
                    # Fallback projection profile splitting for merged line crops
                    if unpadded_height > 1.25 * target_height:
                        sub_bboxes = split_merged_crop_by_projection(col_crop, line_obj.bbox, target_height=target_height)
                    else:
                        sub_bboxes = [line_obj.bbox]

                    for sub_idx, sub_bbox in enumerate(sub_bboxes):
                        slx1, sly1, slx2, sly2 = sub_bbox
                        
                        # Convert to absolute coordinates of pil_img
                        slx1_abs = slx1 + c_xmin
                        sly1_abs = sly1 + c_ymin
                        slx2_abs = slx2 + c_xmin
                        sly2_abs = sly2 + c_ymin

                        # Phase 3: Segment-Level Sub-Block Slicing for wavy columns
                        best_block = find_best_block(sly1_abs, sly2_abs, col.get("blocks", []))
                        if best_block is not None:
                            b_xmin, _, b_xmax, _ = best_block["bbox"]
                            slx1_abs = b_xmin
                            slx2_abs = b_xmax
                        elif "unpadded_bbox" in col:
                            slx1_abs = col["unpadded_bbox"][0]
                            slx2_abs = col["unpadded_bbox"][2]

                        # Crop, pad, and normalize
                        line_crop, padded_bbox = crop_pad_normalize_line(
                            pil_img, [slx1_abs, sly1_abs, slx2_abs, sly2_abs], padding_x=5, padding_y=3
                        )

                        # Run line OCR to verify Cherokee presence
                        line_ocr_text = ocr_image_to_text(line_crop, lang="chr")
                        analysis = analyze_text(line_ocr_text)
                        
                        if analysis["cherokee_count"] < 5:
                            continue

                        # Ensure unique v2 ID and file name
                        line_id = f"{prefix}_col_{col_idx:02d}_line_{line_idx:03d}"
                        if len(sub_bboxes) > 1:
                            line_id += f"_split_{sub_idx:02d}"
                        line_id += "_v2"
                        filename = f"{line_id}.png"

                        # Save crop
                        line_crop_path = os.path.join(crops_dir, filename)
                        line_crop.save(line_crop_path)

                        # Record in manifest
                        new_manifest[line_id] = {
                            "id": line_id,
                            "image_path": f"line_crops/{filename}",
                            "source_scan": rel_path,
                            "column_index": col_idx,
                            "line_index": line_idx,
                            "line_bbox": padded_bbox,
                            "initial_ocr": line_ocr_text.strip(),
                            "label": "",
                            "status": "unlabeled",
                            "crop_version": "v2"
                        }
                        v2_lines_extracted += 1

        print(f"  Extracted {v2_lines_extracted} new v2 Cherokee line crops.")
        v2_completed.add(rel_path)

        # Periodically save manifest and completed set to avoid losing progress
        with open(output_manifest_path, "w", encoding="utf-8") as f:
            json.dump(new_manifest, f, indent=2, ensure_ascii=False)
        with open(completed_scans_path, "w", encoding="utf-8") as f:
            json.dump(list(v2_completed), f, indent=2, ensure_ascii=False)

    print("\nv2 Manifest extraction and migration complete!")
    print(f"Total entries in manifest.json: {len(new_manifest)}")

if __name__ == "__main__":
    main()

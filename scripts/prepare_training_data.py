#!/usr/bin/env python3
import os
import sys
import argparse
import json
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import extract_columns, crop_pad_skew_correct
from server.process_file import ocr_image_to_text
from scripts.classify_layout import analyze_text
from surya.detection import DetectionPredictor

def find_scans(base_dir):
    supported = (".jp2", ".png", ".jpg", ".jpeg", ".tiff", ".bmp")
    scan_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(supported):
                scan_files.append(os.path.join(root, f))
    return sorted(scan_files)

def main():
    parser = argparse.ArgumentParser(
        description="Extract Cherokee text lines from scans to prepare training dataset."
    )
    parser.add_argument("--input-dir", default="scans", help="Directory containing scanned issues")
    parser.add_argument("--output-dir", default="training_data", help="Output folder for training data")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of scans to process (0 = all)")
    parser.add_argument("--padding-y", type=int, default=3, help="Top/bottom padding in pixels for line crops")
    parser.add_argument("--padding-x", type=int, default=5, help="Left/right padding in pixels for line crops")
    parser.add_argument("--overwrite", action="store_true", help="Re-process scans even if they are in the manifest")
    args = parser.parse_args()

    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory '{args.input_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Setup directories
    os.makedirs(args.output_dir, exist_ok=True)
    crops_dir = os.path.join(args.output_dir, "line_crops")
    os.makedirs(crops_dir, exist_ok=True)

    manifest_path = os.path.join(args.output_dir, "manifest.json")
    manifest = {}

    # Load existing manifest if not overwriting
    if os.path.exists(manifest_path) and not args.overwrite:
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"Loaded existing manifest with {len(manifest)} line crops.")
        except Exception as e:
            print(f"Failed to read existing manifest: {e}. Starting fresh.")

    # Find scans
    scans = find_scans(args.input_dir)
    print(f"Found {len(scans)} scan images in '{args.input_dir}' recursively.")

    # Keep track of already processed scans based on completed_scans.json and manifest
    completed_scans_path = os.path.join(args.output_dir, "completed_scans.json")
    completed_scans = set()

    if os.path.exists(completed_scans_path) and not args.overwrite:
        try:
            with open(completed_scans_path, "r", encoding="utf-8") as f:
                completed_scans = set(json.load(f))
            print(f"Loaded {len(completed_scans)} completed scans from {completed_scans_path}.")
        except Exception as e:
            print(f"Failed to read completed scans list: {e}.")

    if not completed_scans and not args.overwrite:
        for item in manifest.values():
            if isinstance(item, dict) and "source_scan" in item:
                completed_scans.add(item["source_scan"])
        if completed_scans:
            print(f"Inferred {len(completed_scans)} completed scans from existing manifest.")

    # Find the first unfinished scan in the sorted sequence
    start_idx = 0
    if not args.overwrite:
        for idx, scan_path in enumerate(scans):
            rel_path = os.path.relpath(scan_path, args.input_dir)
            if rel_path not in completed_scans:
                start_idx = idx
                break
        else:
            start_idx = len(scans)

    scans_to_process = []
    for scan_path in scans[start_idx:]:
        rel_path = os.path.relpath(scan_path, args.input_dir)
        scans_to_process.append((scan_path, rel_path))

    if args.limit > 0:
        scans_to_process = scans_to_process[:args.limit]

    if not scans_to_process:
        print("No new scans to process.")
        sys.exit(0)

    # Initialize line detector
    print("Initializing Surya DetectionPredictor...")
    detector = DetectionPredictor()

    print(f"Processing {len(scans_to_process)} scans starting from sequence index {start_idx + 1}...")

    for idx, (scan_path, rel_path) in enumerate(scans_to_process, 1):
        print(f"\n[{idx}/{len(scans_to_process)}] Processing scan: {rel_path}")
        path_parts = rel_path.replace(os.sep, "_")
        prefix = os.path.splitext(path_parts)[0]

        # Clean up any partial crop files and manifest entries for this scan in case of a previous crash
        import glob
        try:
            pattern = os.path.join(crops_dir, f"{prefix}_col_*_line_*.png")
            for partial_file in glob.glob(pattern):
                os.remove(partial_file)
        except Exception as e:
            print(f"  Warning: Failed to clean up partial crop files: {e}", file=sys.stderr)

        keys_to_remove = [k for k, v in manifest.items() if isinstance(v, dict) and v.get("source_scan") == rel_path]
        for k in keys_to_remove:
            del manifest[k]

        try:
            pil_img = Image.open(scan_path).convert("RGB")
        except Exception as e:
            print(f"  Failed to open image: {e}", file=sys.stderr)
            continue

        # Step 1: Layout detection to find text columns
        print("  Running layout column detection...")
        try:
            columns = extract_columns(pil_img)
            print(f"  Detected {len(columns)} text columns.")
        except Exception as e:
            print(f"  Layout detection failed: {e}", file=sys.stderr)
            continue

        cherokee_col_count = 0
        for col_idx, col in enumerate(columns):
            # Crop & skew correct column
            try:
                col_crop = crop_pad_skew_correct(pil_img, col["bbox"], margin_x=20, margin_y=20)
            except Exception as e:
                print(f"    Failed to crop/skew-correct Column {col_idx:02d}: {e}", file=sys.stderr)
                continue

            # Classify column language content via OCR
            try:
                col_ocr = ocr_image_to_text(col_crop, lang="chr+eng")
                classification = analyze_text(col_ocr)
                lang_class = classification["classification"]
            except Exception as e:
                print(f"    OCR / Classification failed for Column {col_idx:02d}: {e}", file=sys.stderr)
                continue

            # We are interested in Cherokee and Mixed columns
            if lang_class in ["Cherokee", "Mixed"]:
                cherokee_col_count += 1
                print(f"    Column {col_idx:02d} is {lang_class} (Cherokee: {classification['cherokee_count']}, Latin: {classification['latin_count']}). Segmenting lines...")
                
                # Detect lines inside the column crop
                try:
                    predictions = detector([col_crop])
                    pred = predictions[0]
                    detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
                except Exception as e:
                    print(f"      Line detection failed for Column {col_idx:02d}: {e}", file=sys.stderr)
                    continue

                print(f"      Detected {len(detected_lines)} lines in Column {col_idx:02d}.")

                for line_idx, line in enumerate(detected_lines):
                    lx1, ly1, lx2, ly2 = line.bbox
                    # Add padding
                    lx1_pad = max(0, int(lx1) - args.padding_x)
                    ly1_pad = max(0, int(ly1) - args.padding_y)
                    lx2_pad = min(col_crop.width, int(lx2) + args.padding_x)
                    ly2_pad = min(col_crop.height, int(ly2) + args.padding_y)

                    # Crop line
                    line_crop = col_crop.crop((lx1_pad, ly1_pad, lx2_pad, ly2_pad))
                    line_id = f"{prefix}_col_{col_idx:02d}_line_{line_idx:03d}"
                    filename = f"{line_id}.png"
                    
                    # Run line OCR to get an initial transcription guess
                    line_ocr_text = ocr_image_to_text(line_crop, lang="chr")

                    # Save crop
                    line_crop_path = os.path.join(crops_dir, filename)
                    line_crop.save(line_crop_path)

                    # Save record to manifest
                    manifest[line_id] = {
                        "id": line_id,
                        "image_path": f"line_crops/{filename}",
                        "source_scan": rel_path,
                        "column_index": col_idx,
                        "line_index": line_idx,
                        "line_bbox": [lx1_pad, ly1_pad, lx2_pad, ly2_pad],
                        "initial_ocr": line_ocr_text.strip(),
                        "label": "",
                        "status": "unlabeled"
                    }

        print(f"  Finished scan {rel_path}. Processed {cherokee_col_count} Cherokee/Mixed columns.")

        # Mark scan as completed and save manifest/completed scans list in case of interruption
        completed_scans.add(rel_path)
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            with open(completed_scans_path, "w", encoding="utf-8") as f:
                json.dump(list(completed_scans), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"  Warning: Failed to save progress: {e}", file=sys.stderr)

    print(f"\nDone! Processed training dataset saved to '{args.output_dir}/'")
    print(f"Total line crops in manifest: {len(manifest)}")

if __name__ == "__main__":
    main()

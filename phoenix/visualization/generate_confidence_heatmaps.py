#!/usr/bin/env python3
"""
generate_confidence_heatmaps.py

Loads OCR results from manifest_w_lang.json, matches them back to original page scans,
and overlays bounding boxes colored by OCR confidence score.
Saves premium, high-DPI visualization PNGs to training_data/performance_analysis/.

This script corrects for column offsets to ensure precise bounding box alignment
on the original page scans, and only overlays Cherokee items.
"""

import os
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import Normalize
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from server.layout import extract_columns

def main():
    manifest_path = "training_data/manifest_w_lang.json"
    output_dir = "training_data/performance_analysis"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(manifest_path):
        print(f"Error: {manifest_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading manifest from {manifest_path}...")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Group lines by source_scan (only Cherokee items)
    scans_data = {}
    for item_id, item in manifest.items():
        scan = item.get("source_scan")
        bbox = item.get("line_bbox")
        confidence = item.get("ftm_confidence")
        predicted_lang = item.get("predicted_lang")
        
        # Only process Cherokee items with valid scan path, bboxes, and confidence score
        if predicted_lang == "Cherokee" and scan and bbox and len(bbox) == 4 and confidence is not None:
            if scan not in scans_data:
                scans_data[scan] = []
            scans_data[scan].append({
                "id": item_id,
                "bbox": bbox,
                "confidence": confidence,
                "column_index": item.get("column_index", 0),
                "text": item.get("ftm_ocr", "")
            })

    # Pick top sample scans with lots of lines
    selected_scans = [
        "1828-11-19/seq-2.jp2",
        "1828-03-13/seq-1.jp2",
        "1829-01-21/seq-3.jp2"
    ]

    # Setup premium font/styling
    plt.rcParams['font.sans-serif'] = ['Inter', 'Outfit', 'DejaVu Sans', 'Arial', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'

    for scan_rel_path in selected_scans:
        if scan_rel_path not in scans_data:
            print(f"Warning: Scan '{scan_rel_path}' not found in manifest data. Skipping.")
            continue

        scan_full_path = os.path.join("scans", scan_rel_path)
        if not os.path.exists(scan_full_path):
            print(f"Warning: Scan image file '{scan_full_path}' does not exist. Skipping.")
            continue

        print(f"\nProcessing scan: {scan_rel_path}...")
        lines = scans_data[scan_rel_path]
        
        # Load background page image
        try:
            background_img = Image.open(scan_full_path).convert("RGB")
        except Exception as e:
            print(f"Error loading {scan_full_path}: {e}")
            continue

        orig_w, orig_h = background_img.size
        print(f"Original image size: {orig_w}x{orig_h}, found {len(lines)} Cherokee lines.")

        # Run layout detection to find columns and apply correct offsets
        print("Detecting columns to calculate precise offsets...")
        try:
            columns = extract_columns(background_img)
            print(f"Detected {len(columns)} columns on this page.")
        except Exception as e:
            print(f"Warning: Column layout extraction failed ({e}). Offsets will default to 0.")
            columns = []

        # Convert back to grayscale for premium, elegant heatmap contrast
        background_img_gray = background_img.convert("L")

        # Downsample image for performance and smaller output file size
        scale_factor = 0.4
        new_w = int(orig_w * scale_factor)
        new_h = int(orig_h * scale_factor)
        background_img_resized = background_img_gray.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Plot setup
        fig, ax = plt.subplots(figsize=(12, 18), dpi=200)
        ax.imshow(background_img_resized, cmap='gray', alpha=0.85)
        
        # Set up Colormap: Red (0% confidence) -> Yellow (50%) -> Green (100%)
        cmap = plt.colormaps["RdYlGn"]
        norm = Normalize(vmin=0.0, vmax=100.0)

        # Draw bboxes
        confidences = []
        for line in lines:
            bbox = line["bbox"] # [xmin, ymin, xmax, ymax]
            conf = line["confidence"]
            col_idx = line["column_index"]
            confidences.append(conf)

            # Apply column offsets to get absolute page coordinates
            offset_x = 0
            offset_y = 0
            if col_idx < len(columns):
                c_xmin, c_ymin, _, _ = columns[col_idx]["bbox"]
                offset_x = max(0, c_xmin - 20)
                offset_y = max(0, c_ymin - 20)

            abs_xmin = bbox[0] + offset_x
            abs_ymin = bbox[1] + offset_y
            abs_xmax = bbox[2] + offset_x
            abs_ymax = bbox[3] + offset_y

            # Scale coordinates to resized image space
            x = abs_xmin * scale_factor
            y = abs_ymin * scale_factor
            w = (abs_xmax - abs_xmin) * scale_factor
            h = (abs_ymax - abs_ymin) * scale_factor

            # Map confidence score to color
            color = cmap(norm(conf))

            # Add bounding box patch with semi-transparent fill and solid border
            rect = patches.Rectangle(
                (x, y), w, h,
                linewidth=1.2,
                edgecolor=color,
                facecolor=color,
                alpha=0.35
            )
            ax.add_patch(rect)

        # Calculate metrics
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        low_conf_count = sum(1 for c in confidences if c < 70.0)

        # Premium Title and Metadata overlay
        scan_id = scan_rel_path.replace("/", "_").replace(".jp2", "")
        ax.set_title(f"OCR Confidence Heatmap (Cherokee Only): {scan_rel_path}", fontsize=18, fontweight='bold', pad=15)
        ax.axis("off")

        # Colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', pad=0.03, shrink=0.7)
        cbar.set_label("OCR Prediction Confidence (%)", fontsize=12, fontweight='semibold', labelpad=8)
        cbar.ax.tick_params(labelsize=10)

        # Stats text box
        stats_text = (
            f"Cherokee Lines: {len(lines)}\n"
            f"Average Confidence: {avg_conf:.1f}%\n"
            f"Low Confidence (<70%): {low_conf_count} lines"
        )
        ax.text(
            0.03, 0.03, stats_text,
            transform=ax.transAxes,
            fontsize=12,
            fontweight='semibold',
            color='black',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='white',
                edgecolor='#cccccc',
                alpha=0.9
            )
        )

        # Save output
        output_file_name = f"ocr_confidence_heatmap_{scan_id}.png"
        output_path = os.path.join(output_dir, output_file_name)
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=200)
        plt.close(fig)
        print(f"Saved heatmap to: {output_path}")

    print("\nHeatmap generation complete!")

if __name__ == "__main__":
    main()

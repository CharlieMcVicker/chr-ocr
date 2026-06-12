#!/usr/bin/env python
"""
This module previews and visualizes bounding boxes of text columns.
It uses Surya layout predictions, groups text blocks fuzzily into vertical column groups,
applies quality filtering (minimum block counts and column height thresholds), and saves
the visual bounding box overlays to disk.
"""
import os
import sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.layout import get_layout_predictor

def main():
    """
    Main command-line entry point. Extracts columns for one or more scan paths,
    applies the fuzzy layout grouping and filtering, and outputs annotated overlay images
    if --overlay is requested.
    """
    parser = argparse.ArgumentParser(description="Preview bounding boxes of columns.")
    parser.add_argument("scans", nargs='+', help="Paths to sample scan images.")
    parser.add_argument("--overlay", action="store_true", help="Overlay valid column bounding boxes on the image and save to disk.")
    args = parser.parse_args()

    layout_predictor = get_layout_predictor()

    for scan_path in args.scans:
        if not os.path.exists(scan_path):
            print(f"File not found: {scan_path}")
            continue

        print(f"\n--- Processing {os.path.basename(scan_path)} ---")
        try:
            pil_img = Image.open(scan_path).convert("RGB")
        except Exception as e:
            print(f"Failed to open image: {e}")
            continue

        width, height = pil_img.size
        print(f"Image size: {width}x{height}")

        # Extract blocks
        predictions = layout_predictor([pil_img])[0]
        blocks = []
        for block in predictions.bboxes:
            if block.label in ["Text", "List"]:
                blocks.append({
                    "bbox": block.bbox,
                    "label": block.label
                })

        print(f"Raw text blocks detected: {len(blocks)}")

        if not blocks:
            continue

        # Fuzzy grouping
        tolerance = width * 0.08
        groups = []
        for block in blocks:
            xmin, ymin, xmax, ymax = block["bbox"]
            matched_group = None
            for gp in groups:
                gp_xmin = sum(b["bbox"][0] for b in gp) / len(gp)
                gp_xmax = sum(b["bbox"][2] for b in gp) / len(gp)
                if abs(xmin - gp_xmin) <= tolerance and abs(xmax - gp_xmax) <= tolerance:
                    matched_group = gp
                    break
            
            if matched_group is not None:
                matched_group.append(block)
            else:
                groups.append([block])

        print(f"Columns after initial grouping: {len(groups)}")

        # Filtering
        min_blocks = 3
        min_height_ratio = 0.05
        min_height = height * min_height_ratio

        valid_groups = []
        dropped_groups = []

        for idx, gp in enumerate(groups):
            gp_ymins = [b["bbox"][1] for b in gp]
            gp_ymaxs = [b["bbox"][3] for b in gp]
            gp_height = max(gp_ymaxs) - min(gp_ymins)
            
            if len(gp) < min_blocks and gp_height < min_height:
                dropped_groups.append((idx, len(gp), gp_height))
            else:
                valid_groups.append(gp)

        print(f"Columns after filtering: {len(valid_groups)} (Dropped {len(dropped_groups)} groups)")
        
        if dropped_groups:
            print("Dropped groups details:")
            for d_idx, d_len, d_h in dropped_groups:
                print(f"  Group {d_idx}: {d_len} blocks, height {d_h:.1f}px ({(d_h/height)*100:.1f}%)")

        if args.overlay:
            print(f"Generating overlay plot...")
            fig, ax = plt.subplots(figsize=(width / 300, height / 300), dpi=300)
            ax.imshow(pil_img)
            
            cmap = plt.get_cmap("tab10")
            for i, gp in enumerate(valid_groups):
                gp_xmin = min([b["bbox"][0] for b in gp])
                gp_ymin = min([b["bbox"][1] for b in gp])
                gp_xmax = max([b["bbox"][2] for b in gp])
                gp_ymax = max([b["bbox"][3] for b in gp])
                
                rect = patches.Rectangle(
                    (gp_xmin, gp_ymin), gp_xmax - gp_xmin, gp_ymax - gp_ymin,
                    linewidth=3, edgecolor=cmap(i % 10), facecolor='none', alpha=0.8
                )
                ax.add_patch(rect)
                
                # Add label
                ax.text(gp_xmin, gp_ymin - 20, f"Col {i}", color='white', 
                        bbox=dict(facecolor=cmap(i % 10), alpha=0.8), fontsize=10, weight='bold')

            ax.axis('off')
            
            out_plot = os.path.join(os.path.dirname(scan_path), f"bbox_overlay_{os.path.basename(scan_path)}.png")
            plt.savefig(out_plot, bbox_inches='tight', pad_inches=0)
            print(f"Saved bounding box overlay to {out_plot}")
            plt.close(fig)

if __name__ == "__main__":
    main()

#!/usr/bin/env python
import argparse
import sys
import os
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.layout import extract_columns

def main():
    parser = argparse.ArgumentParser(description="Diagnose column bbox grouping by scatter plotting xmin vs xmax.")
    parser.add_argument("image_path", help="Path to the input image file")
    args = parser.parse_args()

    if not os.path.exists(args.image_path):
        print(f"Error: File '{args.image_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading image from {args.image_path}...")
    try:
        pil_img = Image.open(args.image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}", file=sys.stderr)
        sys.exit(1)

    print("Running layout detection...")
    blocks = extract_columns(pil_img)

    if not blocks:
        print("No 'Text' or 'List' bounding boxes detected.")
        sys.exit(0)

    print(f"Detected {len(blocks)} bounding boxes.")

    # Grouping logic from plot_layout.py
    width, height = pil_img.size
    tolerance = width * 0.08
    print(f"Grouping bounding boxes fuzzily with tolerance: {tolerance:.1f} pixels (8% of image width)...")

    groups = []
    block_to_group = []
    for block in blocks:
        xmin, ymin, xmax, ymax = block["bbox"]
        matched_group_idx = None
        for i, gp in enumerate(groups):
            gp_xmin = sum(b["bbox"][0] for b in gp) / len(gp)
            gp_xmax = sum(b["bbox"][2] for b in gp) / len(gp)
            if abs(xmin - gp_xmin) <= tolerance and abs(xmax - gp_xmax) <= tolerance:
                matched_group_idx = i
                break
        
        if matched_group_idx is not None:
            groups[matched_group_idx].append(block)
            block_to_group.append(matched_group_idx)
        else:
            groups.append([block])
            block_to_group.append(len(groups) - 1)

    print(f"Grouped {len(blocks)} boxes into {len(groups)} columns.")

    # Generate scatter plot
    plt.figure(figsize=(10, 10))

    # Plot unmerged bounding boxes colored by their assigned group
    cmap = plt.get_cmap("tab20")
    for idx, block in enumerate(blocks):
        xmin = block["bbox"][0]
        xmax = block["bbox"][2]
        group_idx = block_to_group[idx]
        color = cmap(group_idx % 20)
        plt.scatter(xmin, xmax, color=color, alpha=0.7, edgecolors='black', s=50)
        plt.text(xmin, xmax, str(idx), fontsize=8, alpha=0.7)

    # Plot the merged column centers (average xmin, xmax)
    for i, gp in enumerate(groups):
        gp_xmin = sum(b["bbox"][0] for b in gp) / len(gp)
        gp_xmax = sum(b["bbox"][2] for b in gp) / len(gp)
        color = cmap(i % 20)
        plt.scatter(gp_xmin, gp_xmax, color=color, marker='X', s=200, edgecolors='black', label=f'Col {i}' if len(groups) <= 10 else None)

    # Reference line y = x
    max_val = max([b["bbox"][2] for b in blocks] + [b["bbox"][0] for b in blocks]) if blocks else 100
    plt.plot([0, max_val], [0, max_val], color='gray', linestyle='--', alpha=0.5, label='y = x')

    plt.title(f'Bounding Box X Coordinates (Tolerance: {tolerance:.1f}px)\n{len(blocks)} boxes -> {len(groups)} columns')
    plt.xlabel('xmin (pixels)')
    plt.ylabel('xmax (pixels)')
    
    if len(groups) <= 10:
        plt.legend()
        
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()

    out_plot = os.path.join(os.path.dirname(args.image_path), "bbox_scatter.png")
    plt.savefig(out_plot)
    print(f"Saved scatter plot to {out_plot}")
    print("Showing plot...")
    plt.show()

if __name__ == "__main__":
    main()

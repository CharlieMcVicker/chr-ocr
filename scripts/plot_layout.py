#!/usr/bin/env python
import argparse
import sys
from PIL import Image
import matplotlib.pyplot as plt

# Ensure server package can be imported if script is run from project root or scripts directory
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import detect_and_fix_skew, extract_columns, crop_pad_skew_correct


def main():
    parser = argparse.ArgumentParser(description="Run layout detection and plot bounding box x coordinates.")
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

    # 1. Run detect_and_fix_skew (Disabled as requested)
    print("Skew detection and correction disabled. Processing image directly...")
    processed_img = pil_img

    # 2. Run layout detection
    print("Running layout detection...")
    blocks = extract_columns(processed_img)

    if not blocks:
        print("No 'Text' or 'List' bounding boxes detected.")
        sys.exit(0)

    print(f"Detected {len(blocks)} bounding boxes.")

    # 3. Group bounding boxes fuzzily by xmin/xmax
    # Two boxes are grouped if their xmin and xmax are within a tolerance (e.g. 8% of image width)
    width, height = processed_img.size
    tolerance = width * 0.08
    print(f"Grouping bounding boxes fuzzily with tolerance: {tolerance:.1f} pixels (8% of image width)...")

    groups = []
    for block in blocks:
        xmin, ymin, xmax, ymax = block["bbox"]
        matched_group = None
        for gp in groups:
            # Check against the group's average xmin and xmax
            gp_xmin = sum(b["bbox"][0] for b in gp) / len(gp)
            gp_xmax = sum(b["bbox"][2] for b in gp) / len(gp)
            if abs(xmin - gp_xmin) <= tolerance and abs(xmax - gp_xmax) <= tolerance:
                matched_group = gp
                break
        if matched_group is not None:
            matched_group.append(block)
        else:
            groups.append([block])

    print(f"Grouped {len(blocks)} boxes into {len(groups)} columns.")

    margin_x = 20
    margin_y = 20

    # 4a. Process and save unmerged boxes
    unmerged_blocks = []
    print(f"Processing unmerged bounding boxes (applying margins, cropping, and skew correcting)...")
    for idx, block in enumerate(blocks):
        print(f"Box {idx:03d}: Running crop, pad, and skew correction...")
        cropped_skew_corrected = crop_pad_skew_correct(processed_img, block["bbox"], margin_x, margin_y)
        
        padded_bbox = [
            max(0, block["bbox"][0] - margin_x),
            max(0, block["bbox"][1] - margin_y),
            min(width, block["bbox"][2] + margin_x),
            min(height, block["bbox"][3] + margin_y)
        ]
        
        unmerged_blocks.append({
            "bbox": padded_bbox,
            "image": cropped_skew_corrected
        })

    # 4b. Process and save merged columns
    merged_blocks = []
    print(f"Processing merged column boxes (applying margins, cropping, and skew correcting)...")
    for idx, gp in enumerate(groups):
        gp_xmins = [b["bbox"][0] for b in gp]
        gp_ymins = [b["bbox"][1] for b in gp]
        gp_xmaxs = [b["bbox"][2] for b in gp]
        gp_ymaxs = [b["bbox"][3] for b in gp]
        
        raw_merged_bbox = [min(gp_xmins), min(gp_ymins), max(gp_xmaxs), max(gp_ymaxs)]
        
        print(f"Column {idx:03d}: Running crop, pad, and skew correction...")
        cropped_skew_corrected = crop_pad_skew_correct(processed_img, raw_merged_bbox, margin_x, margin_y)
        
        padded_bbox = [
            max(0, raw_merged_bbox[0] - margin_x),
            max(0, raw_merged_bbox[1] - margin_y),
            min(width, raw_merged_bbox[2] + margin_x),
            min(height, raw_merged_bbox[3] + margin_y)
        ]
        
        merged_blocks.append({
            "bbox": padded_bbox,
            "image": cropped_skew_corrected
        })

    # 5. Save cropped boxes/columns to target folders
    input_dir = os.path.dirname(os.path.abspath(args.image_path))
    input_filename = os.path.basename(args.image_path)
    base_name, _ = os.path.splitext(input_filename)
    
    # Save columns
    columns_dir = os.path.join(input_dir, f"{base_name}-columns")
    import shutil
    if os.path.exists(columns_dir):
        shutil.rmtree(columns_dir)
    os.makedirs(columns_dir, exist_ok=True)
    
    print(f"Saving merged cropped columns to {columns_dir}...")
    for idx, block in enumerate(merged_blocks):
        crop_path = os.path.join(columns_dir, f"column_{idx:03d}.png")
        block["image"].save(crop_path)

    # Save boxes
    boxes_dir = os.path.join(input_dir, f"{base_name}-boxes")
    if os.path.exists(boxes_dir):
        shutil.rmtree(boxes_dir)
    os.makedirs(boxes_dir, exist_ok=True)
    
    print(f"Saving unmerged cropped boxes to {boxes_dir}...")
    for idx, block in enumerate(unmerged_blocks):
        crop_path = os.path.join(boxes_dir, f"box_{idx:03d}.png")
        block["image"].save(crop_path)

    # 5. Extract xmin and xmax of merged blocks
    xmins = [block["bbox"][0] for block in merged_blocks]
    xmaxs = [block["bbox"][2] for block in merged_blocks]

    # 6. Generate scatter plot
    plt.figure(figsize=(8, 8))
    
    # Scatter plot of xmin vs xmax
    plt.scatter(xmins, xmaxs, color='purple', alpha=0.7, edgecolors='black', s=100, label='Merged Column')

    # Draw reference line y = x
    max_val = max(max(xmins), max(xmaxs)) if xmins else 100
    plt.plot([0, max_val], [0, max_val], color='gray', linestyle='--', alpha=0.5, label='y = x')

    plt.title('Merged Bounding Box X Coordinates: xmin vs xmax')
    
    # Label xmin in red
    plt.xlabel('xmin (pixels)', color='red', fontsize=12)
    plt.tick_params(axis='x', labelcolor='red')
    
    # Label xmax in blue
    plt.ylabel('xmax (pixels)', color='blue', fontsize=12)
    plt.tick_params(axis='y', labelcolor='blue')

    plt.legend()
    plt.grid(True, which='both', linestyle='--', alpha=0.3)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.tight_layout()

    print("Showing plot...")
    plt.show()

if __name__ == "__main__":
    main()

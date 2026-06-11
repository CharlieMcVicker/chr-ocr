#!/usr/bin/env python3
import os
import json
import random
import cv2
import numpy as np
import doxapy
import argparse
import sys

def normalize_height(image, target_line_height=42, pad_y=3):
    img_height, img_width = image.shape[:2]
    if img_height == 0 or img_width == 0:
        return image
    
    line_height = max(1, img_height - 2 * pad_y)
    ratio = target_line_height / float(line_height)
    
    target_height = int(round(ratio * img_height))
    target_width = int(round(ratio * img_width))
    
    if target_width == 0: target_width = 1
    if target_height == 0: target_height = 1
    
    resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return resized

def generate_box_file(box_path, text, width, height):
    with open(box_path, "w", encoding="utf-8") as f:
        f.write(f"WordStr 0 0 {width} {height} 0 #{text}\n")
        f.write(f"\t 0 0 {width} {height} 0\n")

def augment_geometry_and_noise(image):
    variations = []
    height, width = image.shape[:2]
    
    # 1. Base (Original)
    variations.append(("base", image))
    
    # 2. Rotation -2 deg
    M_neg = cv2.getRotationMatrix2D((width / 2, height / 2), -2.0, 1.0)
    rot_neg = cv2.warpAffine(image, M_neg, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    variations.append(("rot_neg2", rot_neg))
    
    # 3. Rotation +2 deg
    M_pos = cv2.getRotationMatrix2D((width / 2, height / 2), 2.0, 1.0)
    rot_pos = cv2.warpAffine(image, M_pos, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    variations.append(("rot_pos2", rot_pos))
    
    # 4. Gaussian Noise on base
    noise = np.zeros_like(image)
    cv2.randn(noise, 0, 15)
    noisy_base = cv2.add(image, noise, dtype=cv2.CV_8U)
    variations.append(("noise", noisy_base))
    
    return variations

def binarize(img, algo_name):
    # Convert to grayscale if not already
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    h, w = img.shape[:2]
    # Dynamically scale window size to prevent doxapy crashes on small images
    max_window = (min(h, w) // 2) * 2 + 1
    if max_window < 3:
        max_window = 3

    if algo_name == "otsu":
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary
    elif algo_name == "su":
        algo = doxapy.Binarization.Algorithms.SU
        window = min(75, max_window)
        return doxapy.to_binary(algo, img, {"window": window})
    elif algo_name == "sauvola":
        algo = doxapy.Binarization.Algorithms.SAUVOLA
        window = min(55, max_window)
        return doxapy.to_binary(algo, img, {"window": window, "k": 0.3})
    elif algo_name == "wolf":
        algo = doxapy.Binarization.Algorithms.WOLF
        window = min(45, max_window)
        return doxapy.to_binary(algo, img, {"window": window})
    else:
        return img

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data_v2/manifest_w_lang.json")
    parser.add_argument("--output-dir", default="training_data_v2/dataset")
    parser.add_argument("--split", type=float, default=0.6, help="Train split ratio (e.g. 0.6 for 60/40)")
    parser.add_argument("--pad-y", type=int, default=3, help="Y padding used when crops were generated")
    args = parser.parse_args()

    if not os.path.exists(args.manifest):
        print(f"Manifest not found: {args.manifest}")
        sys.exit(1)

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Filter for Cherokee labeled items
    labeled_items = [
        item for item in manifest.values()
        if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
    ]

    if not labeled_items:
        print("No Cherokee labeled items found.")
        sys.exit(1)

    # Shuffle and split
    random.seed(42) # For reproducibility
    random.shuffle(labeled_items)
    
    split_idx = int(len(labeled_items) * args.split)
    train_items = labeled_items[:split_idx]
    test_items = labeled_items[split_idx:]

    print(f"Found {len(labeled_items)} items. Splitting into {len(train_items)} train and {len(test_items)} test.")

    # Create directories
    train_dir = os.path.join(args.output_dir, "train")
    os.makedirs(train_dir, exist_ok=True)

    binarization_algos = ["otsu", "su", "sauvola", "wolf"]
    test_dirs = {}
    for algo in ["base"] + binarization_algos:
        d = os.path.join(args.output_dir, "test", algo)
        os.makedirs(d, exist_ok=True)
        test_dirs[algo] = d

    # Process Training Data
    print("Processing Training Data...")
    for item in train_items:
        image_path = os.path.join("training_data_v2", item["image_path"])
        img = cv2.imread(image_path)
        if img is None:
            continue

        label = item["label"]
        item_id = item["id"]

        # Geometric & Noise augmentations
        aug_variations = augment_geometry_and_noise(img)

        # For each augmented variation, apply all binarization algos
        for aug_name, aug_img in aug_variations:
            for algo in binarization_algos:
                bin_img = binarize(aug_img, algo)
                norm_img = normalize_height(bin_img, pad_y=args.pad_y)
                h, w = norm_img.shape[:2]
                
                out_name = f"{item_id}_{aug_name}_{algo}"
                out_base = os.path.join(train_dir, out_name)
                
                cv2.imwrite(out_base + ".png", norm_img)
                with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                    f.write(label + "\n")
                generate_box_file(out_base + ".box", label, w, h)

    # Process Test Data
    print("Processing Test Data...")
    for item in test_items:
        image_path = os.path.join("training_data_v2", item["image_path"])
        img = cv2.imread(image_path)
        if img is None:
            continue

        label = item["label"]
        item_id = item["id"]

        # Base Test image (just normalized, grayscale, no binarization)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        norm_gray = normalize_height(gray, pad_y=args.pad_y)
        h, w = norm_gray.shape[:2]
        
        base_out = os.path.join(test_dirs["base"], item_id)
        cv2.imwrite(base_out + ".png", norm_gray)
        with open(base_out + ".gt.txt", "w", encoding="utf-8") as f:
            f.write(label + "\n")
        generate_box_file(base_out + ".box", label, w, h)

        # Binarized Test images (no geometric augmentation)
        for algo in binarization_algos:
            bin_img = binarize(img, algo)
            norm_bin = normalize_height(bin_img, pad_y=args.pad_y)
            
            out_base = os.path.join(test_dirs[algo], item_id)
            cv2.imwrite(out_base + ".png", norm_bin)
            with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                f.write(label + "\n")
            generate_box_file(out_base + ".box", label, w, h)

    print("Done! Dataset generated.")

if __name__ == "__main__":
    main()

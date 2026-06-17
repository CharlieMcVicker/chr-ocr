#!/usr/bin/env python3
"""
This module handles data augmentation and preparation for the Cherokee OCR training dataset.
It performs height normalization, Tesseract box file generation, various geometric/noise
augmentations (including elastic distortion and morphological ink simulation),
and binarization via algorithms like Otsu, Su, Sauvola, and Wolf.
"""
import os
import json
import random
import cv2
import numpy as np
import argparse
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.training.augment import (
    normalize_height,
    generate_box_file,
    augment_geometry_and_noise,
    binarize
)

def main():
    """
    Main function to parse arguments, divide the labeled dataset into train and test splits,
    apply augmentations/binarizations, and write out finalized image, ground-truth,
    and box files.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data/manifest_w_lang.json")
    parser.add_argument("--output-dir", default="training_data/dataset")
    parser.add_argument("--split", type=float, default=0.8, help="Train split ratio")
    parser.add_argument("--pad-y", type=int, default=3, help="Y padding")
    args = parser.parse_args()

    if not os.path.exists(args.manifest):
        print(f"Manifest not found: {args.manifest}")
        sys.exit(1)

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    labeled_items = [
        item for item in manifest.values()
        if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
    ]

    if not labeled_items:
        print("No Cherokee labeled items found.")
        sys.exit(1)

    def should_skip_binarization(item):
        return item.get("dataset") == "cnt"

    # We want to split like "every nth is test" to ensure even distribution across documents
    train_items = []
    test_items = []
    
    accumulator = 0.0
    for item in labeled_items:
        # Check if pre-assigned split field is present
        if "split" in item:
            if item["split"] == "train":
                train_items.append(item)
            elif item["split"] == "test":
                test_items.append(item)
            else:
                # Fallback to train if unrecognized split
                train_items.append(item)
        else:
            # Fallback to dynamic accumulator split
            accumulator += (1.0 - args.split)
            if accumulator >= 1.0:
                test_items.append(item)
                accumulator -= 1.0
            else:
                train_items.append(item)

    print(f"Found {len(labeled_items)} items. Train: {len(train_items)}, Test: {len(test_items)}")

    train_dir = os.path.join(args.output_dir, "train")
    os.makedirs(train_dir, exist_ok=True)

    # Build evaluation grid
    binarization_grid = [("otsu", {})]
    for w in [15, 25, 35, 45]:
        binarization_grid.append((f"su_w{w}", {"algo": "su", "window": w}))
        for k in [0.1, 0.2, 0.3]:
            binarization_grid.append((f"sauvola_w{w}_k{k}", {"algo": "sauvola", "window": w, "k": k}))
            binarization_grid.append((f"wolf_w{w}_k{k}", {"algo": "wolf", "window": w, "k": k}))

    test_dirs = {}
    test_dirs["base"] = os.path.join(args.output_dir, "test", "base")
    os.makedirs(test_dirs["base"], exist_ok=True)
    test_dirs["cnt"] = os.path.join(args.output_dir, "test", "cnt")
    os.makedirs(test_dirs["cnt"], exist_ok=True)

    for grid_name, _ in binarization_grid:
        d = os.path.join(args.output_dir, "test", grid_name)
        os.makedirs(d, exist_ok=True)
        test_dirs[grid_name] = d

    # Process Training Data
    print("Processing Training Data...")
    for item in train_items:
        image_path = os.path.join("training_data", item["image_path"])
        img = cv2.imread(image_path)
        if img is None: continue

        label = item["label"]
        item_id = item["id"]

        aug_variations = augment_geometry_and_noise(img)

        skip_bin = should_skip_binarization(item)

        for aug_name, aug_img in aug_variations:
            if skip_bin:
                # Keep original geometry/noise variation image in its native grayscale/binarized form
                gray_res = cv2.cvtColor(aug_img, cv2.COLOR_BGR2GRAY) if len(aug_img.shape) == 3 else aug_img
                norm_img = normalize_height(gray_res, pad_y=args.pad_y)
                h, w = norm_img.shape[:2]
                
                out_name = f"{item_id}_{aug_name}_native"
                out_base = os.path.join(train_dir, out_name)
                
                cv2.imwrite(out_base + ".png", norm_img)
                with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                    f.write(label + "\n")
                generate_box_file(out_base + ".box", label, w, h)
            else:
                # 1. Otsu
                bin_otsu = binarize(aug_img, "otsu", {})
                # 2. Su (random w)
                w_su = random.choice([15, 25, 35, 45])
                bin_su = binarize(aug_img, "su", {"algo": "su", "window": w_su})
                # 3. Sauvola (random w, k)
                w_sv = random.choice([15, 25, 35, 45])
                k_sv = random.choice([0.1, 0.2, 0.3])
                bin_sv = binarize(aug_img, "sauvola", {"algo": "sauvola", "window": w_sv, "k": k_sv})
                # 4. Wolf (random w, k)
                w_w = random.choice([15, 25, 35, 45])
                k_w = random.choice([0.1, 0.2, 0.3])
                bin_wolf = binarize(aug_img, "wolf", {"algo": "wolf", "window": w_w, "k": k_w})
                
                for alg_name, bin_res in [("otsu", bin_otsu), ("su", bin_su), ("sauvola", bin_sv), ("wolf", bin_wolf)]:
                    norm_img = normalize_height(bin_res, pad_y=args.pad_y)
                    h, w = norm_img.shape[:2]
                    
                    out_name = f"{item_id}_{aug_name}_{alg_name}"
                    out_base = os.path.join(train_dir, out_name)
                    
                    cv2.imwrite(out_base + ".png", norm_img)
                    with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                        f.write(label + "\n")
                    generate_box_file(out_base + ".box", label, w, h)

    # Process Test Data
    print("Processing Test Data...")
    for item in test_items:
        image_path = os.path.join("training_data", item["image_path"])
        img = cv2.imread(image_path)
        if img is None: continue

        label = item["label"]
        item_id = item["id"]

        skip_bin = should_skip_binarization(item)

        if skip_bin:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            norm_gray = normalize_height(gray, pad_y=args.pad_y)
            h, w = norm_gray.shape[:2]
            
            base_out = os.path.join(test_dirs["cnt"], item_id)
            cv2.imwrite(base_out + ".png", norm_gray)
            with open(base_out + ".gt.txt", "w", encoding="utf-8") as f:
                f.write(label + "\n")
            generate_box_file(base_out + ".box", label, w, h)
        else:
            # Base Test image (grayscale)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            norm_gray = normalize_height(gray, pad_y=args.pad_y)
            h, w = norm_gray.shape[:2]
            
            base_out = os.path.join(test_dirs["base"], item_id)
            cv2.imwrite(base_out + ".png", norm_gray)
            with open(base_out + ".gt.txt", "w", encoding="utf-8") as f:
                f.write(label + "\n")
            generate_box_file(base_out + ".box", label, w, h)

            # Grid Test images
            for grid_name, params in binarization_grid:
                bin_img = binarize(img, grid_name, params)
                norm_bin = normalize_height(bin_img, pad_y=args.pad_y)
                h_b, w_b = norm_bin.shape[:2]
                
                out_base = os.path.join(test_dirs[grid_name], item_id)
                cv2.imwrite(out_base + ".png", norm_bin)
                with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                    f.write(label + "\n")
                generate_box_file(out_base + ".box", label, w_b, h_b)

    print("Done! Dataset generated.")

if __name__ == "__main__":
    main()

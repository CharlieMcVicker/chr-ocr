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
    
    # 2. Smooth Rotations
    for i in range(3):
        angle = random.uniform(-3.0, 3.0)
        M = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        rot = cv2.warpAffine(image, M, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        variations.append((f"rot_{i}", rot))
    
    # 3. Gaussian Noise on base
    noise = np.zeros_like(image)
    cv2.randn(noise, 0, 15)
    noisy_base = cv2.add(image, noise, dtype=cv2.CV_8U)
    variations.append(("noise", noisy_base))
    
    return variations

def binarize(img, grid_name, params):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    if grid_name == "otsu":
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    algo_name = params["algo"]
    p = dict(params)
    del p["algo"]
    
    h, w = img.shape[:2]
    max_window = (min(h, w) // 2) * 2 + 1
    if max_window < 3: max_window = 3
    
    if p["window"] > max_window:
        p["window"] = max_window
        
    if algo_name == "su":
        algo = doxapy.Binarization.Algorithms.SU
    elif algo_name == "sauvola":
        algo = doxapy.Binarization.Algorithms.SAUVOLA
    elif algo_name == "wolf":
        algo = doxapy.Binarization.Algorithms.WOLF
    else:
        return img
        
    return doxapy.to_binary(algo, img, p)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data_v2/manifest_w_lang.json")
    parser.add_argument("--output-dir", default="training_data_v2/dataset")
    parser.add_argument("--split", type=float, default=0.6, help="Train split ratio")
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

    # We want to split like "every nth is test" to ensure even distribution across documents
    train_items = []
    test_items = []
    
    accumulator = 0.0
    for item in labeled_items:
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
    for grid_name, _ in binarization_grid:
        d = os.path.join(args.output_dir, "test", grid_name)
        os.makedirs(d, exist_ok=True)
        test_dirs[grid_name] = d

    # Process Training Data
    print("Processing Training Data...")
    for item in train_items:
        image_path = os.path.join("training_data_v2", item["image_path"])
        img = cv2.imread(image_path)
        if img is None: continue

        label = item["label"]
        item_id = item["id"]

        aug_variations = augment_geometry_and_noise(img)

        for aug_name, aug_img in aug_variations:
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
        image_path = os.path.join("training_data_v2", item["image_path"])
        img = cv2.imread(image_path)
        if img is None: continue

        label = item["label"]
        item_id = item["id"]

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

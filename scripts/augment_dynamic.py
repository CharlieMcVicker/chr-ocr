#!/usr/bin/env python3
"""
This module implements advanced dynamic data augmentation for the Cherokee OCR dataset.
It integrates Albumentations to apply sensor noise, spatial distortions, occlusion techniques,
and weakly-supervised synthetic error injection on the training set.
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
    inject_synthetic_errors,
    binarize,
    get_albumentations_pipeline,
    apply_mixup_bleedthrough
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data/manifest_w_lang.json")
    parser.add_argument("--output-dir", required=True, help="Directory to save augmented outputs")
    parser.add_argument("--split", type=float, default=0.6, help="Train split ratio")
    parser.add_argument("--pad-y", type=int, default=3, help="Y padding")
    parser.add_argument("--variations-per-image", type=int, default=3, help="Number of variations per image")
    parser.add_argument("--error-rate", type=float, default=0.05, help="Transcription error injection rate")
    
    # Augmentation options
    parser.add_argument("--blur-prob", type=float, default=0.4)
    parser.add_argument("--shadow-prob", type=float, default=0.3)
    parser.add_argument("--distortion-prob", type=float, default=0.4)
    parser.add_argument("--dropout-prob", type=float, default=0.3)
    parser.add_argument("--bleedthrough-prob", type=float, default=0.25)
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

    # Replicate exact train/test splitting logic
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

    print(f"[Dynamic Augmentation] Total: {len(labeled_items)}. Train (only to be augmented): {len(train_items)}")

    os.makedirs(args.output_dir, exist_ok=True)
    
    # Pre-collect all train image paths for mixup bleed-through
    train_img_paths = []
    for item in train_items:
        path = os.path.join("training_data", item["image_path"])
        if os.path.exists(path):
            train_img_paths.append(path)

    pipeline = get_albumentations_pipeline(
        blur_prob=args.blur_prob,
        shadow_prob=args.shadow_prob,
        distortion_prob=args.distortion_prob,
        dropout_prob=args.dropout_prob
    )

    # Binarization algorithms used dynamically
    bin_methods = ["otsu", "su", "sauvola", "wolf"]

    for idx, item in enumerate(train_items):
        image_path = os.path.join("training_data", item["image_path"])
        img = cv2.imread(image_path)
        if img is None:
            continue

        label = item["label"]
        item_id = item["id"]

        for var_idx in range(args.variations_per_image):
            # 1. Apply Mixup bleed-through
            augmented = apply_mixup_bleedthrough(img, train_img_paths, p=args.bleedthrough_prob)
            
            # 2. Apply Albumentations pipeline
            augmented = pipeline(image=augmented)["image"]
            
            # 3. Dynamic Binarization selection
            algo = random.choice(bin_methods)
            if algo == "otsu":
                bin_res = binarize(augmented, "otsu", {})
            elif algo == "su":
                w = random.choice([15, 25, 35, 45])
                bin_res = binarize(augmented, "su", {"window": w})
            elif algo == "sauvola":
                w = random.choice([15, 25, 35, 45])
                k = random.choice([0.1, 0.2, 0.3])
                bin_res = binarize(augmented, "sauvola", {"window": w, "k": k})
            elif algo == "wolf":
                w = random.choice([15, 25, 35, 45])
                k = random.choice([0.1, 0.2, 0.3])
                bin_res = binarize(augmented, "wolf", {"window": w, "k": k})

            # 4. Normalize height
            norm_img = normalize_height(bin_res, pad_y=args.pad_y)
            h, w = norm_img.shape[:2]

            # 5. Weakly-supervised transcription error injection
            final_label = inject_synthetic_errors(label, error_rate=args.error_rate)

            # 6. Save assets
            out_name = f"{item_id}_dyn_{var_idx}_{algo}"
            out_base = os.path.join(args.output_dir, out_name)

            cv2.imwrite(out_base + ".png", norm_img)
            with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
                f.write(final_label + "\n")
            generate_box_file(out_base + ".box", final_label, w, h)

    print(f"Dynamic augmentation complete. Generated variations in {args.output_dir}")

if __name__ == "__main__":
    main()

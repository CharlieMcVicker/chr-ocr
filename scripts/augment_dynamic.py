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
import doxapy
import argparse
import sys
import albumentations as A

def normalize_height(image, target_line_height=42, pad_y=3):
    """
    Resizes the line image to a target height while maintaining the aspect ratio.
    """
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
    """
    Generates a Tesseract .box file containing WordStr layout format for training.
    """
    with open(box_path, "w", encoding="utf-8") as f:
        f.write(f"WordStr 0 0 {width} {height} 0 #{text}\n")
        f.write(f"\t 0 0 {width} {height} 0\n")

def inject_synthetic_errors(text, error_rate=0.05):
    """
    Probabilistically injects character-level typos (substitution, deletion, insertion)
    into Cherokee transcriptions to simulate label noise and train robust OCR models.
    """
    if random.random() > error_rate or not text:
        return text

    # Common Cherokee syllables to use as random replacements
    cherokee_chars = [chr(c) for c in range(0x13A0, 0x13FF)] + [chr(c) for c in range(0xAB70, 0xABBF)]
    
    chars = list(text)
    err_type = random.choice(["sub", "del", "ins"])
    idx = random.randint(0, len(chars) - 1)
    
    if err_type == "sub" and chars:
        chars[idx] = random.choice(cherokee_chars)
    elif err_type == "del" and len(chars) > 1:
        chars.pop(idx)
    elif err_type == "ins":
        chars.insert(idx, random.choice(cherokee_chars))
        
    return "".join(chars)

def binarize(img, algo_name, params):
    """
    Binarizes an image using Otsu thresholding or local adaptive algorithms via doxapy.
    """
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    if algo_name == "otsu":
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    p = dict(params)
    if "algo" in p:
        del p["algo"]
    
    h, w = img.shape[:2]
    max_window = (min(h, w) // 2) * 2 + 1
    if max_window < 3: max_window = 3
    
    if p.get("window", 15) > max_window:
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

def get_albumentations_pipeline(blur_prob=0.4, shadow_prob=0.3, distortion_prob=0.4, dropout_prob=0.3):
    """
    Constructs a sophisticated Albumentations pipeline for text line perturbation.
    """
    return A.Compose([
        # 1. Sensor Noise
        A.OneOf([
            A.GaussianBlur(blur_limit=(3, 5), p=1.0),
            A.MotionBlur(blur_limit=(3, 5), p=1.0),
            A.MedianBlur(blur_limit=(3, 5), p=1.0),
        ], p=blur_prob),
        A.ImageCompression(quality_range=(40, 85), p=0.3),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.4),
        A.RandomShadow(num_shadows_limit=(1, 2), shadow_dimension=5, p=shadow_prob),
        
        # 2. Spatial Distortions
        A.OneOf([
            A.GridDistortion(num_steps=5, distort_limit=0.1, border_mode=cv2.BORDER_REPLICATE, p=1.0),
            A.ElasticTransform(alpha=1, sigma=15, border_mode=cv2.BORDER_REPLICATE, p=1.0),
        ], p=distortion_prob),
        
        # 3. Occlusion
        A.CoarseDropout(
            num_holes_range=(1, 4),
            hole_height_range=(4, 10),
            hole_width_range=(4, 10),
            fill=255, # fill with white for light background
            p=dropout_prob
        )
    ])

def apply_mixup_bleedthrough(img, train_images, p=0.25):
    """
    Simulates print-through/bleed-through of text from the reverse side of paper.
    Blends a random train line crop into the background at very low opacity.
    """
    if random.random() > p or not train_images:
        return img
        
    bg_img_path = random.choice(train_images)
    bg_img = cv2.imread(bg_img_path)
    if bg_img is None:
        return img
        
    # Resize bg_img to match source img shape
    h, w = img.shape[:2]
    bg_resized = cv2.resize(bg_img, (w, h), interpolation=cv2.INTER_AREA)
    
    # Standardize channels
    if len(img.shape) == 3 and len(bg_resized.shape) == 2:
        bg_resized = cv2.cvtColor(bg_resized, cv2.COLOR_GRAY2BGR)
    elif len(img.shape) == 2 and len(bg_resized.shape) == 3:
        bg_resized = cv2.cvtColor(bg_resized, cv2.COLOR_BGR2GRAY)
        
    # Bleed-through blending: high primary image weight, low background weight
    opacity = random.uniform(0.05, 0.15)
    blended = cv2.addWeighted(img, 1.0 - opacity, bg_resized, opacity, 0)
    return blended

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data/manifest_w_lang.json")
    parser.add_argument("--output-dir", default="training_data/dataset_epoch")
    parser.add_argument("--split", type=float, default=0.8)
    parser.add_argument("--variations-per-image", type=int, default=3)
    parser.add_argument("--error-rate", type=float, default=0.05, help="Weakly supervised synthetic transcription error rate")
    parser.add_argument("--pad-y", type=int, default=3)
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

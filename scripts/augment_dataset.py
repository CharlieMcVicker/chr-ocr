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
import doxapy
import argparse
import sys

def normalize_height(image, target_line_height=42, pad_y=3):
    """
    Resizes the line image to a target height while maintaining the aspect ratio.
    
    Args:
        image: Input OpenCV image.
        target_line_height: The target height in pixels for the text line.
        pad_y: Vertical padding in pixels around the line.
        
    Returns:
        The height-normalized image.
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
    
    Args:
        box_path: Destination path for the .box file.
        text: Ground truth transcription text.
        width: Width of the line image.
        height: Height of the line image.
    """
    with open(box_path, "w", encoding="utf-8") as f:
        f.write(f"WordStr 0 0 {width} {height} 0 #{text}\n")
        f.write(f"\t 0 0 {width} {height} 0\n")

def augment_elastic_distortion(image):
    """Simulate paper warp/curl by applying a smooth random displacement field.

    Uses a low-frequency sinusoidal component combined with a blurred random
    field so the resulting warp looks like gentle paper curl rather than noise.
    Amplitude is kept between 3-6 px to avoid scrambling text.

    Returns a list of (name, image) tuples with 2-3 elastic variants.
    """
    variations = []
    height, width = image.shape[:2]

    for i in range(3):
        amplitude = random.uniform(3.0, 6.0)
        # Phase shifts make each variant unique
        phase_x = random.uniform(0, 2 * np.pi)
        phase_y = random.uniform(0, 2 * np.pi)
        freq = random.uniform(0.5, 1.5)  # spatial frequency (cycles across image)

        # Build coordinate grids
        xs = np.linspace(0, 2 * np.pi * freq, width, dtype=np.float32)
        ys = np.linspace(0, 2 * np.pi * freq, height, dtype=np.float32)
        grid_x, grid_y = np.meshgrid(xs, ys)

        # Sinusoidal base displacement
        dx_sin = amplitude * np.sin(grid_y + phase_x)
        dy_sin = amplitude * np.sin(grid_x + phase_y)

        # Small random perturbation blurred to low frequency
        rand_dx = np.random.randn(height, width).astype(np.float32) * (amplitude * 0.5)
        rand_dy = np.random.randn(height, width).astype(np.float32) * (amplitude * 0.5)
        blur_k = max(3, (min(height, width) // 8) | 1)  # odd kernel
        rand_dx = cv2.GaussianBlur(rand_dx, (blur_k, blur_k), 0)
        rand_dy = cv2.GaussianBlur(rand_dy, (blur_k, blur_k), 0)

        dx = (dx_sin + rand_dx).astype(np.float32)
        dy = (dy_sin + rand_dy).astype(np.float32)

        # Build remap maps: map_x(y,x) = x + dx, map_y(y,x) = y + dy
        base_x, base_y = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
        )
        map_x = (base_x + dx).clip(0, width - 1)
        map_y = (base_y + dy).clip(0, height - 1)

        warped = cv2.remap(
            image, map_x, map_y,
            interpolation=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        variations.append((f"elastic_{i}", warped))

    return variations


def augment_morphological_ink(image):
    """Simulate ink bleed (erode) and ink fade (dilate) on a binarized image.

    Only applied when the image is already binarized (binary pixel distribution).
    Produces 1-2 erode and 1-2 dilate variants with randomised kernel sizes.

    Returns a list of (name, image) tuples, or an empty list if image is not binary.
    """
    variations = []

    # Detect binary image: >90% of pixels are either 0 or 255
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    binary_count = int(np.sum((gray == 0) | (gray == 255)))
    total_pixels = gray.size
    if total_pixels == 0 or binary_count / total_pixels < 0.90:
        return variations  # Not a binary image — skip morphological augmentation

    # Ink bleed: erode (dark ink strokes grow thicker)
    for i in range(2):
        k_size = random.choice([2, 3])
        kernel = np.ones((k_size, k_size), np.uint8)
        eroded = cv2.erode(image, kernel, iterations=1)
        variations.append((f"erode_{i}", eroded))

    # Ink fade: dilate (dark ink strokes thin out)
    for i in range(2):
        k_size = random.choice([2, 3])
        kernel = np.ones((k_size, k_size), np.uint8)
        dilated = cv2.dilate(image, kernel, iterations=1)
        variations.append((f"dilate_{i}", dilated))

    return variations


def augment_geometry_and_noise(image):
    """
    Applies geometric augmentations, Gaussian noise, elastic distortion, and
    morphological ink simulations to generate multiple dataset variants from a single image.
    
    Args:
        image: Source OpenCV image.
        
    Returns:
        List of tuples (variant_name, augmented_image).
    """
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

    # 4. Elastic distortion (paper warp/curl simulation)
    variations.extend(augment_elastic_distortion(image))

    # 5. Morphological ink simulation (applied post-binarization so we pass
    #    binarized versions inline). We generate them here on the raw image
    #    for non-binary cases; the binarize() step downstream will handle the
    #    actual thresholding. For the morphological variants we pre-binarize
    #    with Otsu so the erode/dilate operate on a proper binary image.
    gray_for_morph = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, bin_for_morph = cv2.threshold(gray_for_morph, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    morph_variants = augment_morphological_ink(bin_for_morph)
    variations.extend(morph_variants)
    
    return variations

def binarize(img, grid_name, params):
    """
    Binarizes an image using Otsu thresholding or local adaptive algorithms
    from doxapy (such as Su, Sauvola, or Wolf).
    
    Args:
        img: Input OpenCV image.
        grid_name: Name of the binarization method or grid key.
        params: Dict of parameter settings for doxapy.
        
    Returns:
        The single-channel binary image.
    """
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
    """
    Main function to parse arguments, divide the labeled dataset into train and test splits,
    apply augmentations/binarizations, and write out finalized image, ground-truth,
    and box files.
    """
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

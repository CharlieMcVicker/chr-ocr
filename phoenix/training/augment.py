"""
This module handles data augmentation and preparation for the Cherokee OCR training dataset.
It combines static augmentations (geometric, noise, elastic distortion, morphological ink simulations)
and dynamic augmentations (Albumentations-based pipeline, mixup bleedthrough, synthetic error injection)
with support for various binarization algorithms (Otsu, Su, Sauvola, Wolf).
"""

import os
import json
import random
import cv2
import numpy as np
import doxapy
import albumentations as A

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

    # 5. Morphological ink simulation
    gray_for_morph = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    _, bin_for_morph = cv2.threshold(gray_for_morph, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    morph_variants = augment_morphological_ink(bin_for_morph)
    variations.extend(morph_variants)
    
    return variations

def binarize(img, name, params=None):
    """
    Binarizes an image using Otsu thresholding or local adaptive algorithms via doxapy.
    Unified implementation supporting both static method names and dynamic config mappings.
    """
    if params is None:
        params = {}
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    if name == "otsu":
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        return binary

    algo_name = params.get("algo", name)
    if "_" in algo_name:
        algo_name = algo_name.split("_")[0]
        
    p = dict(params)
    if "algo" in p:
        del p["algo"]
    
    h, w = img.shape[:2]
    max_window = (min(h, w) // 2) * 2 + 1
    if max_window < 3:
        max_window = 3
    
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

def get_albumentations_pipeline(
    blur_prob=0.4,
    shadow_prob=0.3,
    distortion_prob=0.4,
    dropout_prob=0.3,
    blur_limit=(3, 5),
    shadow_dimension=5,
    distortion_limit=0.1,
    dropout_holes_range=(1, 4),
    dropout_size_range=(4, 10),
):
    """
    Constructs a sophisticated Albumentations pipeline for text line perturbation.
    """
    return A.Compose([
        # 1. Sensor Noise
        A.OneOf([
            A.GaussianBlur(blur_limit=blur_limit, p=1.0),
            A.MotionBlur(blur_limit=blur_limit, p=1.0),
            A.MedianBlur(blur_limit=blur_limit, p=1.0),
        ], p=blur_prob),
        A.ImageCompression(quality_range=(40, 85), p=0.3),
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.4),
        A.RandomShadow(num_shadows_limit=(1, 2), shadow_dimension=shadow_dimension, p=shadow_prob),
        
        # 2. Spatial Distortions
        A.OneOf([
            A.GridDistortion(num_steps=5, distort_limit=distortion_limit, border_mode=cv2.BORDER_REPLICATE, p=1.0),
            A.ElasticTransform(alpha=1, sigma=15, border_mode=cv2.BORDER_REPLICATE, p=1.0),
        ], p=distortion_prob),
        
        # 3. Occlusion
        A.CoarseDropout(
            num_holes_range=dropout_holes_range,
            hole_height_range=dropout_size_range,
            hole_width_range=dropout_size_range,
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

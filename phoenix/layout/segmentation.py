"""
Module for layout analysis, column extraction, line detection, skew correction,
and text line cropping/standardization.
"""

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import rotate
from itertools import product
from surya.inference import SuryaInferenceManager
from surya.layout import LayoutPredictor
from surya.detection import DetectionPredictor

def load_image_grayscale(image_input) -> np.ndarray:
    """
    Utility to load image from a file path, a PIL Image, or a numpy array
    and convert it to a grayscale numpy array (2D uint8).
    """
    if isinstance(image_input, str):
        img = cv2.imread(image_input, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not load image from path: {image_input}")
        return img
    elif isinstance(image_input, Image.Image):
        return np.array(image_input.convert("L"))
    elif isinstance(image_input, np.ndarray):
        if len(image_input.shape) == 3:
            if image_input.shape[2] == 3:
                return cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
            elif image_input.shape[2] == 4:
                return cv2.cvtColor(image_input, cv2.COLOR_BGRA2GRAY)
        return image_input.astype(np.uint8)
    else:
        raise TypeError("Unsupported image input type. Must be file path, PIL.Image, or numpy.ndarray.")

def apply_stain_cleaning(
    image_input,
    morph_kernel_size: int,
    gaussian_blur_ksize: int,
    clahe_clip_limit: float,
) -> np.ndarray:
    """
    Applies stain cleaning to an image using morphological closing to estimate
    and cancel background illumination.
    """
    img = load_image_grayscale(image_input)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_kernel_size, morph_kernel_size))
    background = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    if gaussian_blur_ksize > 0:
        if gaussian_blur_ksize % 2 == 0:
            gaussian_blur_ksize += 1
        background = cv2.GaussianBlur(background, (gaussian_blur_ksize, gaussian_blur_ksize), 0)

    normalized = cv2.divide(img, background, scale=255)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=(8, 8))
    return clahe.apply(normalized)

def apply_adaptive_threshold(
    image_input,
    block_size: int = 151,
    c_value: float = 0.0,
    morph_kernel_size: int = 3,
) -> np.ndarray:
    """
    Applies adaptive thresholding (Gaussian C) and morphological opening cleanup.
    """
    img = load_image_grayscale(image_input)
    if block_size % 2 == 0:
        block_size += 1

    doxa_su_result = cv2.adaptiveThreshold(
        img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c_value
    )

    if morph_kernel_size > 0:
        kernel_morph = np.ones((morph_kernel_size, morph_kernel_size), np.uint8)
        doxa_su_result = cv2.morphologyEx(doxa_su_result, cv2.MORPH_OPEN, kernel_morph)

    return doxa_su_result

def run_stain_cleaning_search(
    image_input,
    morph_kernel_sizes: list = None,
    gaussian_blur_ksizes: list = None,
    clahe_clip_limits: list = None,
) -> list:
    """
    Runs a grid search over stain cleaning parameter spaces.
    """
    if morph_kernel_sizes is None:
        morph_kernel_sizes = [51, 101, 151]
    if gaussian_blur_ksizes is None:
        gaussian_blur_ksizes = [0, 11, 21, 31]
    if clahe_clip_limits is None:
        clahe_clip_limits = [2.0, 5.0, 8.0]

    img = load_image_grayscale(image_input)
    results = []

    for morph_k, gauss_k, clahe_c in product(morph_kernel_sizes, gaussian_blur_ksizes, clahe_clip_limits):
        try:
            cleaned = apply_stain_cleaning(img, morph_k, gauss_k, clahe_c)
            results.append({
                "image": cleaned,
                "params": {
                    "morph_kernel_size": morph_k,
                    "gaussian_blur_ksize": gauss_k,
                    "clahe_clip_limit": clahe_c,
                }
            })
        except Exception as e:
            print(f"Error for params morph_k={morph_k}, gauss_k={gauss_k}, clahe={clahe_c}: {e}")

    return results

def detect_and_fix_skew(pil_img: Image.Image) -> Image.Image:
    """
    Detects document skew angle and rotates it back to straight.
    """
    img_gray = np.array(pil_img.convert("L"))

    if np.mean(img_gray) > 127:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    angles = np.linspace(-10, 10, 81)
    best_angle = 0
    max_variance = 0

    for angle in angles:
        rotated = rotate(thresh[::2, ::2], angle, reshape=False, order=0)
        row_sums = np.sum(rotated, axis=1)
        variance = np.var(row_sums)

        if variance > max_variance:
            max_variance = variance
            best_angle = angle

    print(f"Detected document skew angle: {best_angle:.2f}°")

    if abs(best_angle) > 0.2:
        return pil_img.rotate(
            best_angle, resample=Image.BICUBIC, expand=True, fillcolor="white"
        )

    return pil_img

def crop_pad_skew_correct(pil_img: Image.Image, bbox: list, margin_x: int, margin_y: int) -> Image.Image:
    """
    Crops the region, pads, and applies skew correction.
    """
    width, height = pil_img.size
    xmin, ymin, xmax, ymax = bbox

    xmin_pad = max(0, xmin - margin_x)
    ymin_pad = max(0, ymin - margin_y)
    xmax_pad = min(width, xmax + margin_x)
    ymax_pad = min(height, ymax + margin_y)

    cropped = pil_img.crop((xmin_pad, ymin_pad, xmax_pad, ymax_pad))
    return detect_and_fix_skew(cropped)

_layout_predictor = None
_detector = None

def get_layout_predictor():
    """
    Retrieves or initializes a singleton instance of the Surya LayoutPredictor.
    """
    global _layout_predictor
    if _layout_predictor is None:
        print("Initializing Surya layout models...")
        manager = SuryaInferenceManager()
        _layout_predictor = LayoutPredictor(manager)
    return _layout_predictor

def get_detector():
    """
    Retrieves or initializes a singleton instance of the Surya DetectionPredictor.
    """
    global _detector
    if _detector is None:
        print("Initializing Surya detection models...")
        _detector = DetectionPredictor()
    return _detector

def extract_columns_batch(pil_imgs: list) -> list:
    """
    Runs Surya layout detection on a batch of images and groups blocks fuzzily into columns.
    """
    layout_predictor = get_layout_predictor()
    print(f"Analyzing document layout in batch of {len(pil_imgs)}...")
    batch_predictions = layout_predictor(pil_imgs)
    
    batch_columns = []
    for idx, pil_img in enumerate(pil_imgs):
        predictions = batch_predictions[idx]
        if hasattr(predictions, "error") and predictions.error:
            print(f"Warning: Layout prediction failed or returned error for image {idx}. Skipping column grouping.")
            batch_columns.append([])
            continue

        width, height = pil_img.size
        tolerance = width * 0.08
        min_blocks = 3
        min_height = height * 0.05

        blocks = []
        for block in predictions.bboxes:
            if block.label in ["Text", "List"]:
                blocks.append({
                    "bbox": block.bbox,
                    "label": block.label
                })
                
        if not blocks:
            batch_columns.append([])
            continue

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
                
        extracted_columns = []
        for gp in groups:
            gp_ymins = [b["bbox"][1] for b in gp]
            gp_ymaxs = [b["bbox"][3] for b in gp]
            gp_height = max(gp_ymaxs) - min(gp_ymins)
            
            if len(gp) >= min_blocks or gp_height >= min_height:
                gp_xmins = [b["bbox"][0] for b in gp]
                gp_xmaxs = [b["bbox"][2] for b in gp]
                
                merged_bbox = [
                    min(gp_xmins),
                    min(gp_ymins),
                    max(gp_xmaxs),
                    max(gp_ymaxs)
                ]
                
                cropped = pil_img.crop(tuple(merged_bbox))
                extracted_columns.append({
                    "image": cropped,
                    "bbox": merged_bbox,
                    "label": "Column"
                })
                
        extracted_columns.sort(key=lambda c: c["bbox"][0])
        batch_columns.append(extracted_columns)
        
    return batch_columns

def extract_columns(pil_img: Image.Image) -> list:
    """
    Runs Surya layout detection on the image and groups blocks fuzzily into columns.
    """
    return extract_columns_batch([pil_img])[0]

def crop_pad_normalize_line(image, bbox, padding_x, padding_y, target_height_range=(30, 33)):
    """
    Crop a line from an image with padding, and normalize its height.
    """
    lx1, ly1, lx2, ly2 = bbox
    unpadded_height = max(1, int(ly2) - int(ly1))
    target_height = target_height_range[0]
    
    if unpadded_height < 30 or unpadded_height <= 1.5 * target_height:
        lx1_pad = max(0, int(lx1) - padding_x)
        ly1_pad = max(0, int(ly1) - padding_y)
        lx2_pad = min(image.width, int(lx2) + padding_x)
        ly2_pad = min(image.height, int(ly2) + padding_y)
        
        line_crop = image.crop((lx1_pad, ly1_pad, lx2_pad, ly2_pad))
        return line_crop, [lx1_pad, ly1_pad, lx2_pad, ly2_pad]
    else:
        ratio = target_height / unpadded_height
        dynamic_pad_x = int(padding_x / ratio)
        dynamic_pad_y = int(padding_y / ratio)
        
        lx1_pad = max(0, int(lx1) - dynamic_pad_x)
        ly1_pad = max(0, int(ly1) - dynamic_pad_y)
        lx2_pad = min(image.width, int(lx2) + dynamic_pad_x)
        ly2_pad = min(image.height, int(ly2) + dynamic_pad_y)
        
        line_crop = image.crop((lx1_pad, ly1_pad, lx2_pad, ly2_pad))
        
        new_width = int(line_crop.width * ratio)
        new_height = int(line_crop.height * ratio)
        line_crop = line_crop.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return line_crop, [lx1_pad, ly1_pad, lx2_pad, ly2_pad]

def extract_lines_from_images_batch(pil_imgs: list, padding_x: int = 5, padding_y: int = 3, batch_size: int = 16) -> list:
    """
    Extracts columns and then lines from each column in a batch of PIL Images.
    Uses Surya layout and detection predictors cached as singletons.
    """
    detector = get_detector()
    
    # 1. Batch extract columns
    batch_columns = extract_columns_batch(pil_imgs)
    
    # 2. Collect all images that need detection (some have columns, some fall back to full image)
    # We will record tasks to run detector on and their mappings back to the original image index.
    detection_inputs = []
    detection_mapping = []  # List of tuples (img_idx, col_idx, col_crop, col_bbox, is_full_page)
    
    for img_idx, columns in enumerate(batch_columns):
        pil_img = pil_imgs[img_idx]
        if columns:
            for col_idx, col in enumerate(columns):
                margin_x = 20
                margin_y = 20
                c_xmin, c_ymin, c_xmax, c_ymax = col["bbox"]
                c_xmin = max(0, c_xmin - margin_x)
                c_ymin = max(0, c_ymin - margin_y)
                c_xmax = min(pil_img.width, c_xmax + margin_x)
                c_ymax = min(pil_img.height, c_ymax + margin_y)
                
                col_crop = pil_img.crop((c_xmin, c_ymin, c_xmax, c_ymax))
                detection_inputs.append(col_crop)
                detection_mapping.append((img_idx, col_idx, col_crop, col["bbox"], False))
        else:
            detection_inputs.append(pil_img)
            detection_mapping.append((img_idx, 0, pil_img, [0, 0, pil_img.width, pil_img.height], True))
            
    # 3. Batch run line detection on all compiled inputs
    all_predictions = []
    if detection_inputs:
        for offset in range(0, len(detection_inputs), batch_size):
            chunk = detection_inputs[offset:offset + batch_size]
            all_predictions.extend(detector(chunk))
            
    # 4. Reconstruct results per image
    batch_results = [[] for _ in range(len(pil_imgs))]
    
    for pred_idx, pred in enumerate(all_predictions):
        img_idx, col_idx, crop_img, col_bbox, is_full_page = detection_mapping[pred_idx]
        
        if hasattr(pred, "error") and pred.error:
            print(f"Warning: Detection prediction failed or returned error for crop index {pred_idx}. Skipping line extraction.")
            continue

        detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
        lines_data = []
        for line_idx, line in enumerate(detected_lines):
            line_crop, padded_bbox = crop_pad_normalize_line(
                crop_img, line.bbox, padding_x, padding_y
            )
            lines_data.append({
                "image": line_crop,
                "bbox": padded_bbox,
                "confidence": line.confidence,
                "index": line_idx
            })
            
        if not is_full_page:
            batch_results[img_idx].append({
                "column_index": col_idx,
                "column_bbox": col_bbox,
                "column_image": crop_img,
                "lines": lines_data
            })
        else:
            batch_results[img_idx].append({
                "column_index": 0,
                "column_bbox": col_bbox,
                "column_image": crop_img,
                "lines": lines_data
            })
            
    return batch_results

def extract_lines_from_image(pil_img: Image.Image, padding_x: int = 5, padding_y: int = 3) -> list:
    """
    Extracts columns and then lines from each column in a PIL Image.
    Uses Surya layout and detection predictors.
    """
    return extract_lines_from_images_batch([pil_img], padding_x, padding_y)[0]


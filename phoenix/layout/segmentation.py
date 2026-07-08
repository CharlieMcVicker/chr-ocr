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

def compute_dynamic_asymmetric_margins(columns: list, default_margin_x: int = 20) -> list:
    """
    Computes dynamic asymmetric horizontal margins (left and right) for each column in columns list.
    If two columns are very close horizontally, shrink their respective margins proportionally
    to prevent one column's crop from capturing characters belonging to the neighboring column.
    
    Each column dict in columns list should have key 'bbox': [xmin, ymin, xmax, ymax].
    Returns a list of dicts: [{"left": margin_l, "right": margin_r}, ...]
    """
    margins = []
    for i in range(len(columns)):
        c_xmin, _, c_xmax, _ = columns[i]["bbox"]
        
        # Left margin
        margin_l = default_margin_x
        if i > 0:
            _, _, prev_xmax, _ = columns[i-1]["bbox"]
            gutter = c_xmin - prev_xmax
            if gutter > 0:
                if gutter < 2 * default_margin_x:
                    margin_l = max(0, int(gutter // 2))
            else:
                margin_l = 0
                
        # Right margin
        margin_r = default_margin_x
        if i < len(columns) - 1:
            next_xmin, _, _, _ = columns[i+1]["bbox"]
            gutter = next_xmin - c_xmax
            if gutter > 0:
                if gutter < 2 * default_margin_x:
                    margin_r = max(0, int(gutter // 2))
            else:
                margin_r = 0
                
        margins.append({"left": margin_l, "right": margin_r})
    return margins

def find_best_block(ly1_abs, ly2_abs, blocks):
    """
    Find the text block that has the maximum vertical overlap with the line's vertical span,
    falling back to the vertically closest block if there is no overlap.
    """
    if not blocks:
        return None
    best_block = None
    max_overlap = -1
    for block in blocks:
        bx1, by1, bx2, by2 = block["bbox"]
        overlap = max(0, min(ly2_abs, by2) - max(ly1_abs, by1))
        if overlap > max_overlap:
            max_overlap = overlap
            best_block = block
    if max_overlap > 0:
        return best_block
    # Fallback to closest block vertically
    closest_block = min(blocks, key=lambda b: min(abs(ly1_abs - b["bbox"][3]), abs(ly2_abs - b["bbox"][1])))
    return closest_block

def extract_columns_batch(pil_imgs: list) -> list:
    """
    Runs Surya layout detection on a batch of images and groups blocks fuzzily into columns.
    """
    # Phase 1: Global Pre-Straightening Skew Correction
    straight_imgs = [detect_and_fix_skew(img) for img in pil_imgs]
    
    layout_predictor = get_layout_predictor()
    print(f"Analyzing document layout in batch of {len(straight_imgs)}...")
    batch_predictions = layout_predictor(straight_imgs)
    
    batch_columns = []
    for idx, pil_img in enumerate(straight_imgs):
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
                
                extracted_columns.append({
                    "bbox": merged_bbox,
                    "label": "Column",
                    "blocks": gp
                })
                
        extracted_columns.sort(key=lambda c: c["bbox"][0])
        
        # Phase 2: Dynamic Column Margin & Overlap Prevention
        margins = compute_dynamic_asymmetric_margins(extracted_columns, default_margin_x=20)
        
        final_columns = []
        for c_idx, col in enumerate(extracted_columns):
            merged_bbox = col["bbox"]
            margin_l = margins[c_idx]["left"]
            margin_r = margins[c_idx]["right"]
            margin_y = 20
            
            c_xmin, c_ymin, c_xmax, c_ymax = merged_bbox
            c_xmin_pad = max(0, c_xmin - margin_l)
            c_ymin_pad = max(0, c_ymin - margin_y)
            c_xmax_pad = min(pil_img.width, c_xmax + margin_r)
            c_ymax_pad = min(pil_img.height, c_ymax + margin_y)
            
            cropped = pil_img.crop((c_xmin_pad, c_ymin_pad, c_xmax_pad, c_ymax_pad))
            
            final_columns.append({
                "image": cropped,
                "bbox": [c_xmin_pad, c_ymin_pad, c_xmax_pad, c_ymax_pad],
                "label": "Column",
                "blocks": col["blocks"],
                "unpadded_bbox": merged_bbox
            })
            
        batch_columns.append(final_columns)
        
    return batch_columns

def extract_columns(pil_img: Image.Image) -> list:
    """
    Runs Surya layout detection on the image and groups blocks fuzzily into columns.
    """
    return extract_columns_batch([pil_img])[0]

def split_merged_crop_by_projection(crop_img, bbox, target_height=30) -> list:
    """
    Split a merged line crop using secondary horizontal projection profile analysis.
    Converts the crop image region defined by bbox to grayscale, binarizes it,
    computes row sums to find white-space valleys between text lines, and
    calculates split boundaries.
    
    Returns a list of absolute sub-bboxes relative to the coordinate space of crop_img.
    """
    xmin, ymin, xmax, ymax = bbox
    xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
    
    width = max(1, xmax - xmin)
    height = max(1, ymax - ymin)
    
    # Crop the merged region from the image
    line_crop = crop_img.crop((xmin, ymin, xmax, ymax))
    img_gray = np.array(line_crop.convert("L"))
    
    # Binarize so text pixels are 255 and background pixels are 0
    if np.mean(img_gray) > 127:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    row_sums = np.sum(thresh, axis=1)
    
    # Identify valleys. A row is a valley if its sum is very low (e.g. less than 1% of max possible sum)
    threshold = width * 255 * 0.01
    active_rows = np.where(row_sums > threshold)[0]
    
    blocks = []
    if len(active_rows) > 0:
        # Group consecutive active rows into text line blocks
        start = active_rows[0]
        for i in range(1, len(active_rows)):
            if active_rows[i] > active_rows[i-1] + 1:
                blocks.append((start, active_rows[i-1]))
                start = active_rows[i]
        blocks.append((start, active_rows[-1]))
    
    # Filter out blocks that are too thin to be a real line (e.g. < 5 pixels high)
    valid_blocks = [b for b in blocks if (b[1] - b[0] + 1) >= 5]
    if not valid_blocks and blocks:
        valid_blocks = blocks
        
    splits = []
    if len(valid_blocks) > 1:
        # Calculate split boundaries at the midpoints of valleys between consecutive blocks
        for i in range(len(valid_blocks) - 1):
            end_current = valid_blocks[i][1]
            start_next = valid_blocks[i+1][0]
            splits.append(int((end_current + start_next) // 2))
    else:
        # Fallback/Enhancement: If simple thresholding yielded 1 or fewer blocks,
        # but the height is > 1.25 * target_height, use local minima valley detection.
        if height > 1.25 * target_height:
            # Smooth row_sums with a moving average of window 5 to reduce noise
            window_size = 5
            smoothed = np.convolve(row_sums.astype(float), np.ones(window_size)/window_size, mode='same')
            
            # Find local minima
            # A point i is a local minimum if it is the minimum in a local window of size 15
            # and is not too close to the edges (at least 10 pixels away)
            local_minima = []
            win = 15
            margin = 10
            for i in range(margin, len(smoothed) - margin):
                start_w = max(0, i - win // 2)
                end_w = min(len(smoothed), i + win // 2 + 1)
                if smoothed[i] == np.min(smoothed[start_w:end_w]):
                    # Calculate depth/prominence: min of max to the left and max to the right, minus value
                    left_max = np.max(smoothed[:i]) if i > 0 else 0
                    right_max = np.max(smoothed[i:]) if i < len(smoothed) - 1 else 0
                    depth = min(left_max, right_max) - smoothed[i]
                    local_minima.append((i, depth))
            
            # Determine how many splits we want based on expected line count
            num_expected_lines = max(2, int(round(height / target_height)))
            num_splits_needed = num_expected_lines - 1
            
            if local_minima:
                # Sort by depth descending and select top num_splits_needed
                local_minima.sort(key=lambda x: x[1], reverse=True)
                selected_splits = [item[0] for item in local_minima[:num_splits_needed]]
                splits = sorted(selected_splits)
                
    if not splits:
        return [bbox]
        
    # Construct sub-bboxes in the absolute coordinates of crop_img
    sub_bboxes = []
    current_ymin = int(ymin)
    for s in splits:
        split_y = int(ymin + s)
        sub_bboxes.append([int(xmin), int(current_ymin), int(xmax), int(split_y)])
        current_ymin = split_y
    sub_bboxes.append([int(xmin), int(current_ymin), int(xmax), int(ymax)])
    
    return sub_bboxes

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
    
    # Phase 1: Global Pre-Straightening Skew Correction
    straight_imgs = [detect_and_fix_skew(img) for img in pil_imgs]
    
    # 1. Batch extract columns
    batch_columns = extract_columns_batch(straight_imgs)
    
    # 2. Collect all images that need detection (some have columns, some fall back to full image)
    # We will record tasks to run detector on and their mappings back to the original image index.
    detection_inputs = []
    detection_mapping = []  # List of tuples (img_idx, col_idx, col_crop, col_bbox, is_full_page, (c_xmin_pad, c_ymin_pad))
    
    for img_idx, columns in enumerate(batch_columns):
        pil_img = straight_imgs[img_idx]
        if columns:
            for col_idx, col in enumerate(columns):
                c_xmin, c_ymin, _, _ = col["bbox"]
                col_crop = col["image"]
                detection_inputs.append(col_crop)
                detection_mapping.append((img_idx, col_idx, col_crop, col["bbox"], False, (c_xmin, c_ymin)))
        else:
            detection_inputs.append(pil_img)
            detection_mapping.append((img_idx, 0, pil_img, [0, 0, pil_img.width, pil_img.height], True, (0, 0)))
            
    # 3. Batch run line detection on all compiled inputs
    all_predictions = []
    if detection_inputs:
        for offset in range(0, len(detection_inputs), batch_size):
            chunk = detection_inputs[offset:offset + batch_size]
            all_predictions.extend(detector(chunk))
            
    # 4. Reconstruct results per image
    batch_results = [[] for _ in range(len(pil_imgs))]
    
    for pred_idx, pred in enumerate(all_predictions):
        img_idx, col_idx, crop_img, col_bbox, is_full_page, (c_xmin_pad, c_ymin_pad) = detection_mapping[pred_idx]
        pil_img = straight_imgs[img_idx]
        columns = batch_columns[img_idx]
        col = columns[col_idx] if (columns and not is_full_page) else None
        
        if hasattr(pred, "error") and pred.error:
            print(f"Warning: Detection prediction failed or returned error for crop index {pred_idx}. Skipping line extraction.")
            continue

        detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
        lines_data = []
        line_idx_counter = 0
        for line in detected_lines:
            lx1, ly1, lx2, ly2 = line.bbox
            unpadded_height = max(1, int(ly2) - int(ly1))
            target_height = 30
            
            if unpadded_height > 1.25 * target_height:
                # Merge crop too tall, apply horizontal projection splitting
                sub_bboxes = split_merged_crop_by_projection(crop_img, line.bbox, target_height=target_height)
                for sub_bbox in sub_bboxes:
                    slx1, sly1, slx2, sly2 = sub_bbox
                    
                    # Convert to absolute coordinates relative to pil_img
                    slx1_abs = slx1 + c_xmin_pad
                    sly1_abs = sly1 + c_ymin_pad
                    slx2_abs = slx2 + c_xmin_pad
                    sly2_abs = sly2 + c_ymin_pad
                    
                    # Phase 3: Segment-Level Sub-Block Slicing for Columns
                    if col:
                        best_block = find_best_block(sly1_abs, sly2_abs, col.get("blocks", []))
                        if best_block is not None:
                            b_xmin, _, b_xmax, _ = best_block["bbox"]
                            slx1_abs = b_xmin
                            slx2_abs = b_xmax
                        else:
                            slx1_abs = col["unpadded_bbox"][0]
                            slx2_abs = col["unpadded_bbox"][2]
                    
                    line_crop, padded_bbox = crop_pad_normalize_line(
                        pil_img, [slx1_abs, sly1_abs, slx2_abs, sly2_abs], padding_x, padding_y
                    )
                    
                    # Convert padded_bbox back to relative coordinates of the column crop
                    rel_padded_bbox = [
                        padded_bbox[0] - c_xmin_pad,
                        padded_bbox[1] - c_ymin_pad,
                        padded_bbox[2] - c_xmin_pad,
                        padded_bbox[3] - c_ymin_pad
                    ]
                    
                    lines_data.append({
                        "image": line_crop,
                        "bbox": rel_padded_bbox,
                        "confidence": line.confidence,
                        "index": line_idx_counter
                    })
                    line_idx_counter += 1
            else:
                # Convert to absolute coordinates relative to pil_img
                lx1_abs = lx1 + c_xmin_pad
                ly1_abs = ly1 + c_ymin_pad
                lx2_abs = lx2 + c_xmin_pad
                ly2_abs = ly2 + c_ymin_pad
                
                # Phase 3: Segment-Level Sub-Block Slicing for Columns
                if col:
                    best_block = find_best_block(ly1_abs, ly2_abs, col.get("blocks", []))
                    if best_block is not None:
                        b_xmin, _, b_xmax, _ = best_block["bbox"]
                        lx1_abs = b_xmin
                        lx2_abs = b_xmax
                    else:
                        lx1_abs = col["unpadded_bbox"][0]
                        lx2_abs = col["unpadded_bbox"][2]
                
                line_crop, padded_bbox = crop_pad_normalize_line(
                    pil_img, [lx1_abs, ly1_abs, lx2_abs, ly2_abs], padding_x, padding_y
                )
                
                # Convert padded_bbox back to relative coordinates of the column crop
                rel_padded_bbox = [
                    padded_bbox[0] - c_xmin_pad,
                    padded_bbox[1] - c_ymin_pad,
                    padded_bbox[2] - c_xmin_pad,
                    padded_bbox[3] - c_ymin_pad
                ]
                
                lines_data.append({
                    "image": line_crop,
                    "bbox": rel_padded_bbox,
                    "confidence": line.confidence,
                    "index": line_idx_counter
                })
                line_idx_counter += 1
            
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


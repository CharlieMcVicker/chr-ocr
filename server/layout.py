import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import rotate
from itertools import product
from surya.inference import SuryaInferenceManager
from surya.layout import LayoutPredictor


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
            # If shape is (H, W, C), convert using OpenCV
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
    Applies stain cleaning to an image (path, PIL Image, or numpy array)
    using morphological closing to estimate and cancel background illumination.
    
    Args:
        image_input: File path, PIL.Image, or numpy array.
        morph_kernel_size: Size of the morph kernel (must be odd).
        gaussian_blur_ksize: Size of Gaussian blur kernel (odd, or 0 to skip).
        clahe_clip_limit: Clip limit for CLAHE contrast enhancement.
        
    Returns:
        A cleaned grayscale numpy array (uint8).
    """
    img = load_image_grayscale(image_input)

    # Create a large kernel to blur/erase the text, leaving only the water stain
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (morph_kernel_size, morph_kernel_size))

    # Estimate the background illumination/stain profile
    background = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    # Further smooth the background using a Gaussian blur to reduce harsh illumination lines
    if gaussian_blur_ksize > 0:
        if gaussian_blur_ksize % 2 == 0:
            gaussian_blur_ksize += 1  # Make it odd if even
        background = cv2.GaussianBlur(background, (gaussian_blur_ksize, gaussian_blur_ksize), 0)

    # Divide original image by background to cancel out the dark stain
    normalized = cv2.divide(img, background, scale=255)

    # Apply standard CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=(8, 8))
    final_grayscale = clahe.apply(normalized)

    return final_grayscale


def apply_adaptive_threshold(
    image_input,
    block_size: int = 151,
    c_value: float = 0.0,
    morph_kernel_size: int = 3,
) -> np.ndarray:
    """
    Applies adaptive thresholding (Gaussian C) and morphological opening cleanup.
    
    Args:
        image_input: File path, PIL.Image, or numpy array.
        block_size: Size of a pixel neighborhood (must be odd).
        c_value: Constant subtracted from the mean.
        morph_kernel_size: Size of the structuring element for morphological opening.
        
    Returns:
        A binary numpy array (0 and 255) of the same size.
    """
    img = load_image_grayscale(image_input)

    # Ensure block_size is odd
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
    
    Returns:
        A list of dicts: [{"image": np.ndarray, "params": dict}, ...]
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
    # Convert PIL Image to a grayscale numpy array for analysis
    img_gray = np.array(pil_img.convert("L"))

    # Threshold the image to make text white (255) and background black (0).
    # This prevents scipy.ndimage.rotate's default black boundary padding (cval=0)
    # from skewing the row-sum variance calculation.
    if np.mean(img_gray) > 127:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # We use a variance-of-projections method to find the best angle
    # This checks which rotation yields the sharpest horizontal text line profiles
    angles = np.linspace(-10, 10, 81)  # Search between -10 and +10 degrees
    best_angle = 0
    max_variance = 0

    for angle in angles:
        # Rotate a downscaled version for speed
        rotated = rotate(thresh[::2, ::2], angle, reshape=False, order=0)
        # Sum along rows to get a projection profile
        row_sums = np.sum(rotated, axis=1)
        variance = np.var(row_sums)

        if variance > max_variance:
            max_variance = variance
            best_angle = angle

    print(f"Detected document skew angle: {best_angle:.2f}°")

    if abs(best_angle) > 0.2:  # Only rotate if the tilt is noticeable
        # Rotate the original PIL image (using white background expansion)
        return pil_img.rotate(
            best_angle, resample=Image.BICUBIC, expand=True, fillcolor="white"
        )

    return pil_img


def crop_pad_skew_correct(pil_img: Image.Image, bbox: list, margin_x: int, margin_y: int) -> Image.Image:
    """
    Takes a PIL image and a bounding box [xmin, ymin, xmax, ymax],
    applies margins, crops the region, and applies skew correction.
    """
    width, height = pil_img.size
    xmin, ymin, xmax, ymax = bbox

    # Pad/apply margin
    xmin_pad = max(0, xmin - margin_x)
    ymin_pad = max(0, ymin - margin_y)
    xmax_pad = min(width, xmax + margin_x)
    ymax_pad = min(height, ymax + margin_y)

    # Crop
    cropped = pil_img.crop((xmin_pad, ymin_pad, xmax_pad, ymax_pad))

    # Skew correct
    return detect_and_fix_skew(cropped)



_layout_predictor = None

def get_layout_predictor():
    global _layout_predictor
    if _layout_predictor is None:
        print("Initializing Surya layout models...")
        manager = SuryaInferenceManager()
        _layout_predictor = LayoutPredictor(manager)
    return _layout_predictor


def extract_columns(pil_img: Image.Image) -> list:
    """
    Runs Surya layout detection on the image, groups the blocks fuzzily into columns,
    filters out noise, and crops/returns the combined text/list columns.
    
    Returns:
        A list of dicts containing the cropped PIL.Image and its bounding box details:
        [{"image": PIL.Image, "bbox": [xmin, ymin, xmax, ymax], "label": str}, ...]
    """
    layout_predictor = get_layout_predictor()

    print("Analyzing document layout...")
    predictions = layout_predictor([pil_img])[0]
    
    width, height = pil_img.size
    tolerance = width * 0.08
    min_blocks = 3
    min_height = height * 0.05

    # 1. Extract raw Text/List blocks
    blocks = []
    for block in predictions.bboxes:
        if block.label in ["Text", "List"]:
            blocks.append({
                "bbox": block.bbox,
                "label": block.label
            })
            
    if not blocks:
        return []

    # 2. Fuzzy grouping by xmin/xmax
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
            
    # 3. Filter small/noisy groups and merge
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
            
            # Crop to the merged bounding box to maintain same return signature
            cropped = pil_img.crop(tuple(merged_bbox))
            extracted_columns.append({
                "image": cropped,
                "bbox": merged_bbox,
                "label": "Column"
            })
            
    # Sort columns left-to-right
    extracted_columns.sort(key=lambda c: c["bbox"][0])
    
    return extracted_columns

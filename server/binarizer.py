import cv2
import numpy as np
import doxapy
from PIL import Image

def preprocess_and_binarize_cv2(img, algorithm_name, parameters=None, use_bg_sub=True, use_bilateral=True, use_cc_denoise=True):
    """
    Core function to preprocess and binarize a grayscale OpenCV image (numpy array).
    """
    # For small images (like individual line crops), local thresholding with large windows
    # is prone to edge-effect noise and memory/segmentation crashes in doxapy.
    # We fall back to OpenCV Otsu thresholding for these images.
    if img.shape[0] < 60 or img.shape[1] < 60:
        _, otsu = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return otsu

    # 1. Background subtraction/normalization (illumination correction)
    if use_bg_sub:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (71, 71))
        background = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        img = cv2.divide(img, background, scale=255)

    # 2. Denoising
    if use_bilateral:
        denoised = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    else:
        denoised = cv2.GaussianBlur(img, (3, 3), 0)

    # 3. Choose algorithm
    name_lower = algorithm_name.lower()
    if name_lower == 'su':
        algo = doxapy.Binarization.Algorithms.SU
        default_params = {"window": 75}
    elif name_lower == 'sauvola':
        algo = doxapy.Binarization.Algorithms.SAUVOLA
        default_params = {"window": 55, "k": 0.3}
    elif name_lower == 'wolf':
        algo = doxapy.Binarization.Algorithms.WOLF
        default_params = {"window": 45}
    else:
        raise ValueError(f"Unsupported binarization algorithm: {algorithm_name}")

    if parameters:
        default_params.update(parameters)

    # Run thresholding
    binary_output = doxapy.to_binary(algo, denoised, default_params)

    # 4. Clean up post-thresholding
    if use_cc_denoise:
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_output, connectivity=8)
        clean_binary = np.ones_like(binary_output) * 255
        for label in range(1, num_labels):
            area = stats[label, cv2.CC_STAT_AREA]
            if area >= 10:  # Ignore components smaller than 10 pixels
                clean_binary[labels == label] = 0
        cleaned_binary = clean_binary
    else:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned_binary = cv2.morphologyEx(binary_output, cv2.MORPH_OPEN, kernel)

    return cleaned_binary


def binarize_image(input_path, output_path, algorithm_name, parameters=None, use_bg_sub=True, use_bilateral=True, use_cc_denoise=True):
    """
    Binarize an image file using doxapy and save the output.
    """
    # 1. Load the image using OpenCV in Grayscale
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {input_path}")

    cleaned_binary = preprocess_and_binarize_cv2(
        img, algorithm_name, parameters, use_bg_sub, use_bilateral, use_cc_denoise
    )

    # Save the processed image
    cv2.imwrite(output_path, cleaned_binary)


def binarize_pil_image(pil_img, algorithm_name="sauvola", parameters=None, use_bg_sub=True, use_bilateral=True, use_cc_denoise=True):
    """
    Binarize a PIL image in-memory and return a new PIL Image.
    """
    # Convert PIL Image to OpenCV Grayscale
    open_cv_image = np.array(pil_img)
    if len(open_cv_image.shape) == 3:
        img = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
    else:
        img = open_cv_image

    cleaned_binary = preprocess_and_binarize_cv2(
        img, algorithm_name, parameters, use_bg_sub, use_bilateral, use_cc_denoise
    )

    # Convert back to PIL Image
    return Image.fromarray(cleaned_binary)


"""
Local adaptive binarization handlers for historic document images.

This module exposes preprocessing, adaptive thresholding, and noise reduction
interfaces around the doxapy library, supporting algorithms:
- SU (Su, Lu, and Tan) local thresholding.
- Sauvola local thresholding.
- Wolf local thresholding.

Includes preprocessing filters (background subtraction and bilateral/Gaussian smoothing)
and postprocessing filters (connected-component based denoising and morphological opening).
"""

import cv2
import numpy as np
import doxapy
from PIL import Image

def preprocess_and_binarize_cv2(img, algorithm_name, parameters=None, use_bg_sub=True, use_bilateral=True, use_cc_denoise=True):
    """
    Core function to preprocess and binarize a grayscale OpenCV image (numpy array).

    Preprocesses images to equalize illumination and minimize noise, applies the selected
    local thresholding binarization algorithm, and cleans up residual noise.

    Args:
        img (np.ndarray): Input 2D grayscale image array (uint8).
        algorithm_name (str): Local thresholding algorithm name ('su', 'sauvola', or 'wolf').
        parameters (dict, optional): Custom parameter overrides for the selected algorithm (e.g. window size).
        use_bg_sub (bool, optional): If True, applies morphological closing division for background subtraction.
            Defaults to True.
        use_bilateral (bool, optional): If True, applies bilateral filtering; otherwise Gaussian blurring.
            Defaults to True.
        use_cc_denoise (bool, optional): If True, filters out small disconnected component noise. Defaults to True.

    Returns:
        np.ndarray: Binary image (numpy array) containing only values 0 and 255.

    Raises:
        ValueError: If an unsupported algorithm_name is specified.
    """
    # For small images (like individual line crops), local thresholding with large windows
    # can crash doxapy if the window exceeds image dimensions. We will clamp the window below.

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

    # Ensure window size is odd and does not exceed image dimensions
    if "window" in default_params:
        max_win = min(img.shape[0], img.shape[1])
        if max_win % 2 == 0:
            max_win -= 1
        if max_win < 3:
            max_win = 3
        if default_params["window"] > max_win:
            default_params["window"] = max_win

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

    Args:
        input_path (str): File path of the input grayscale source image.
        output_path (str): File path to save the processed binary output image.
        algorithm_name (str): Algorithm name to apply ('su', 'sauvola', or 'wolf').
        parameters (dict, optional): Custom algorithm parameters dictionary. Defaults to None.
        use_bg_sub (bool, optional): If True, performs background subtraction. Defaults to True.
        use_bilateral (bool, optional): If True, performs bilateral noise filtering. Defaults to True.
        use_cc_denoise (bool, optional): If True, filters out tiny pixel noise components. Defaults to True.

    Raises:
        FileNotFoundError: If the input_path image fails to load.
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

    This function automatically casts the PIL Image representation to a NumPy grayscale array,
    applies the pre-processing and thresholding pipeline, and wraps the resulting binary
    matrix back into a PIL Image instance.

    Args:
        pil_img (PIL.Image.Image): The input source PIL Image object.
        algorithm_name (str, optional): Algorithm name to apply. Defaults to "sauvola".
        parameters (dict, optional): Custom parameters overrides. Defaults to None.
        use_bg_sub (bool, optional): If True, performs background subtraction. Defaults to True.
        use_bilateral (bool, optional): If True, performs bilateral filtering. Defaults to True.
        use_cc_denoise (bool, optional): If True, filters out pixel-level noise. Defaults to True.

    Returns:
        PIL.Image.Image: The resulting processed binary PIL Image object.
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

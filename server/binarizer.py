import cv2
import numpy as np
import doxapy

def binarize_image(input_path, output_path, algorithm_name, parameters=None):
    """
    Binarize an image using doxapy and save the output.
    Supported algorithms: 'su', 'sauvola', 'wolf'
    """
    # 1. Load the image using OpenCV in Grayscale
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {input_path}")

    # 2. Denoise slightly to eliminate old paper grain noise
    blurred = cv2.GaussianBlur(img, (3, 3), 0)

    # 4. Choose algorithm
    name_lower = algorithm_name.lower()
    if name_lower == 'su':
        algo = doxapy.Binarization.Algorithms.SU
        default_params = {"window": 75}
    elif name_lower == 'sauvola':
        algo = doxapy.Binarization.Algorithms.SAUVOLA
        default_params = {"window": 45, "k": 0.2}
    elif name_lower == 'wolf':
        algo = doxapy.Binarization.Algorithms.WOLF
        default_params = {"window": 45}
    else:
        raise ValueError(f"Unsupported binarization algorithm: {algorithm_name}")

    if parameters:
        default_params.update(parameters)

    # Run thresholding
    binary_output = doxapy.to_binary(algo, blurred, default_params)

    # 5. Clean up post-thresholding
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned_binary = cv2.morphologyEx(binary_output, cv2.MORPH_OPEN, kernel)

    # 6. Save the processed image
    cv2.imwrite(output_path, cleaned_binary)

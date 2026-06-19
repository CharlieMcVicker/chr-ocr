---
id: doc-1
title: Doxa Binarization Spec
type: specification
created_date: '2026-06-10 14:39'
updated_date: '2026-06-10 14:39'
---
The `DIGI-VUB/image.binarization` repository is actually an **R package wrapper** around an underlying high-performance C++ framework called **$\Delta$oxa (Doxa)**, written by Brandon Petty.

If you want to plug these exact, high-end algorithms (like Su, Wolf, and Bataineh) directly into a **Python pipeline**, you should use **`doxapy`**, which is the official Python binding for that exact same C++ engine. It processes images lightning-fast using SIMD optimizations (SSE2/AVX/ARM NEON) and interfaces perfectly with `NumPy`, `Pillow`, and `OpenCV`.

The implementation process requires installing the library and integrating it into your Python pipeline.

### Step 1: Install `doxapy`

You can install the official Python bindings directly via pip:

```bash
pip install doxapy opencv-python

```

---

### Step 2: The Python Pipeline Script

This pipeline reads your newspaper scan using OpenCV, uses `doxapy` to apply advanced binarization (like the Su or Sauvola methods), converts the result back into a standard NumPy array, and runs Tesseract on it.

```python
import cv2
import numpy as np
import doxapy
import pytesseract

def preprocess_and_ocr(image_path):
    # 1. Load the image using OpenCV in Grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {image_path}")

    # 2. Denoise slightly to eliminate old paper grain noise
    # (Crucial step for water-damaged newspapers before thresholding)
    blurred = cv2.GaussianBlur(img, (3, 3), 0)

    # 3. Initialize the DoxaPy Binarization Engine
    # Doxa handles the memory management between Python and C++
    binary_output = np.empty_like(blurred)

    # 4. Choose your algorithm.
    # For severe water damage/fading, Su or Sauvola are top-tier.
    # Algorithms available: .SU, .SAUVOLA, .WOLF, .NIBLACK, .GATOS, .BERNSEN
    algo = doxapy.Binarization.Algorithms.SU

    # Run the thresholding. Parameters are passed as a dictionary.
    # For SU: 'window' parameter dictates local neighborhood size (default is usually fine)
    doxapy.to_binary(algo, blurred, binary_output, {"window": 75})

    # 5. Optional: Quick clean up post-thresholding
    # (Removes isolated 1-2 pixel micro-specks caused by water stains)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned_binary = cv2.morphologyEx(binary_output, cv2.MORPH_OPEN, kernel)

    # 6. Feed directly into Tesseract OCR
    # `--psm 3` tells Tesseract to look for a full page of text with automatic layout
    custom_config = r'--oem 3 --psm 3'
    ocr_text = pytesseract.image_to_string(cleaned_binary, config=custom_config)

    # Save the processed image so you can visually inspect the threshold quality
    cv2.imwrite('preprocessed_for_tesseract.png', cleaned_binary)

    return ocr_text

# --- Run the pipeline ---
if __name__ == "__main__":
    image_file = "water_damaged_newspaper.jpg"
    try:
        text = preprocess_and_ocr(image_file)
        print("--- OCR RESULT ---")
        print(text)
    except Exception as e:
        print(f"Error: {e}")

```

---

### Tuning Parameters for Ancient/Damaged Text

Because `doxapy` hooks into the native C++ library, you can easily swap algorithms and tweak their dictionaries in step 4 to see what gives Tesseract the cleanest characters.

- **The `SU` Method (`doxapy.Binarization.Algorithms.SU`):** Best for ink bleed-through and fading text. It focuses heavily on text stroke contours.
- _Parameters:_ `{"window": 75}` (Increase the window size if the text is huge; decrease it to `35` or `45` if it's very tiny newspaper print).

- **The `SAUVOLA` Method (`doxapy.Binarization.Algorithms.SAUVOLA`):** The industry baseline for stained paper.
- _Parameters:_ `{"window": 45, "k": 0.2}` (Lowering `k` to `0.1` makes the threshold more sensitive, bringing out faded characters; raising it to `0.3` strips away more aggressive water stains).

- **The `WOLF` Method (`doxapy.Binarization.Algorithms.WOLF`):**
  An improvement over Sauvola when the text contrast changes drastically from the top of the page to the bottom.

How severe is the fading on your scans? If the text is practically invisible in some spots, we might need to apply a local contrast stretch before sending it to `doxapy`.

"""
Processing pipeline orchestrator for document scans.

This module coordinates:
- Image normalization and rescaling (to standard max bounds).
- Morphological and background stain cleaning via scripts.
- Multi-algorithm local binarization (su, sauvola, wolf) utilizing doxapy.
- Line bounding box extraction and hOCR document Generation via Tesseract OCR.
- Unified multi-format conversion pipelines.
"""

import os
import subprocess
import re
import shutil
from server.binarizer import binarize_image, binarize_pil_image


def normalize_image(src_path: str, target_path: str, delete_source_if_different: bool = False) -> None:
    """
    Transcode and downscale image to a max of 2400px on the longest side.
    
    If delete_source_if_different is True and target_path != src_path,
    delete the src_path after successful transcode.

    Args:
        src_path (str): File path of the source image to normalize.
        target_path (str): Destination file path to save the normalized image.
        delete_source_if_different (bool, optional): If True and target_path is different,
            removes the source file. Defaults to False.

    Raises:
        RuntimeError: If image transcoding/resizing fails under both system binaries.
    """
    try:
        subprocess.run(
            [
                "magick",
                "convert",
                src_path,
                "-resize",
                "2400x2400>",
                target_path,
            ],
            check=True,
        )
    except Exception:
        # Fallback to convert
        try:
            subprocess.run(
                [
                    "convert",
                    src_path,
                    "-resize",
                    "2400x2400>",
                    target_path,
                ],
                check=True,
            )
        except Exception as e:
            raise RuntimeError(f"Image transcode/resize failed: {str(e)}")

    if delete_source_if_different and target_path != src_path:
        try:
            os.remove(src_path)
        except Exception:
            pass


def clean_image_with_script(input_path: str, output_path: str) -> None:
    """
    Cleans an image using the scripts/clean-img script, estimating and
    removing noise, stains, and lighting shadows.

    Args:
        input_path (str): File path to the source image.
        output_path (str): File path to save the cleaned output image.

    Raises:
        RuntimeError: If the shell script execution encounters an error.
        FileNotFoundError: If the script completes but output is missing.
    """
    server_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(server_dir)
    clean_script_path = os.path.join(project_root, "scripts", "clean-img")

    input_path_rel = os.path.relpath(input_path, project_root)

    try:
        subprocess.run(
            [clean_script_path, input_path_rel],
            cwd=project_root,
            check=True,
        )
    except Exception as e:
        raise RuntimeError(f"Clean image script failed: {str(e)}")

    # The script outputs to <input_path>-out.png
    cleaned_out_path = input_path + "-out.png"
    if not os.path.exists(cleaned_out_path):
        raise FileNotFoundError(f"Cleaned image not found at expected path: {cleaned_out_path}")

    # Move to the desired output_path
    shutil.move(cleaned_out_path, output_path)

    # Clean up temp files from clean-img script
    for tmp_suffix in ["-tmp.png", "-tmp2.png", "-tmp3.png"]:
        tmp_file = input_path + tmp_suffix
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass


def run_doxa_binarization(input_path: str, output_path: str, algorithm: str) -> None:
    """
    Runs Doxa binarization (su, sauvola, wolf) on the input image.

    Args:
        input_path (str): File path to the grayscale source image.
        output_path (str): Destination path to save the binary output image.
        algorithm (str): Doxa binarization algorithm name ('su', 'sauvola', or 'wolf').

    Raises:
        RuntimeError: If binarization fails or encounters invalid parameters.
    """
    try:
        binarize_image(input_path, output_path, algorithm)
    except Exception as e:
        raise RuntimeError(f"Doxa binarization ({algorithm}) failed: {str(e)}")


def ocr_image_to_text(pil_img, lang: str = "chr+eng", binarize: bool = True) -> str:
    """
    Runs Tesseract OCR on a PIL image and returns the recognized text.

    Args:
        pil_img (PIL.Image.Image): PIL Image to perform OCR on.
        lang (str, optional): Tesseract language model code(s). Defaults to "chr+eng".
        binarize (bool, optional): If True, preprocesses the image using Doxa's
            Sauvola binarization before OCR. Defaults to True.

    Returns:
        str: Recognized plaintext string. Returns an empty string on failure.
    """
    import tempfile
    from PIL import Image
    
    if binarize:
        try:
            pil_img = binarize_pil_image(pil_img)
        except Exception as e:
            print(f"Error during binarization preprocessing: {e}")
            # Fall back to original image on binarization failure
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_img_path = tmp.name
    
    try:
        pil_img.save(temp_img_path)
        result = subprocess.run(
            ["tesseract", "--dpi", "300", "-l", lang, temp_img_path, "stdout"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except Exception as e:
        # Fallback/log
        print(f"Error during Tesseract OCR: {e}")
        return ""
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except Exception:
                pass


def get_tesseract_line_bboxes(pil_img, lang: str = "chr+eng") -> list:
    """
    Runs Tesseract OCR on a PIL image and extracts bounding boxes for each detected line.

    Args:
        pil_img (PIL.Image.Image): The input PIL Image.
        lang (str, optional): Tesseract language model. Defaults to "chr+eng".

    Returns:
        list: A list of tuples containing line bounding boxes: [(xmin, ymin, xmax, ymax), ...]
    """
    import tempfile
    import csv
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_img_path = tmp.name
        
    try:
        pil_img.save(temp_img_path)
        result = subprocess.run(
            ["tesseract", "--dpi", "300", "-l", lang, temp_img_path, "stdout", "tsv"],
            capture_output=True,
            text=True,
            check=True,
        )
        
        bboxes = []
        reader = csv.DictReader(result.stdout.splitlines(), delimiter='\t')
        for row in reader:
            if row.get("level") == "4":  # Line level
                left = int(row["left"])
                top = int(row["top"])
                width = int(row["width"])
                height = int(row["height"])
                if width > 0 and height > 0:
                    bboxes.append((left, top, left + width, top + height))
                    
        return bboxes
    except Exception as e:
        print(f"Error during Tesseract TSV extraction: {e}")
        return []
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except Exception:
                pass


def run_tesseract_ocr(input_path: str, output_html_path: str, image_title: str) -> None:
    """
    Runs tesseract OCR on input_path and writes modified hOCR content to output_html_path.

    This function updates the generated hOCR HTML so that browser-based viewers
    reference the correct localized image filename instead of absolute system paths.

    Args:
        input_path (str): Path to the image file to run OCR on.
        output_html_path (str): Destination path to save the modified hOCR HTML.
        image_title (str): Image filename or title to embed inside hOCR header structure.

    Raises:
        RuntimeError: If Tesseract fails or outputs bad data.
        FileNotFoundError: If the hOCR output file cannot be retrieved.
    """
    out_dir = os.path.dirname(output_html_path)
    os.makedirs(out_dir, exist_ok=True)

    # Generate a unique temp base name in the same directory
    temp_base = os.path.join(out_dir, f"temp_ocr_{os.path.basename(input_path)}")
    temp_hocr = temp_base + ".hocr"

    try:
        subprocess.run(
            ["tesseract", "--dpi", "300", "-l", "chr", input_path, temp_base, "hocr"],
            check=True,
        )
    except Exception as e:
        raise RuntimeError(f"OCR processing on {os.path.basename(input_path)} failed: {str(e)}")

    if not os.path.exists(temp_hocr):
        raise FileNotFoundError(f"hOCR output file not found at {temp_hocr}")

    # Read the hOCR content and rewrite the image title path
    try:
        with open(temp_hocr, "r", encoding="utf-8") as f:
            hocr_content = f.read()

        hocr_content = re.sub(r'image\s+"[^"]+"', f'image "{image_title}"', hocr_content)

        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(hocr_content)
    finally:
        # Clean up temp hOCR file
        if os.path.exists(temp_hocr):
            try:
                os.remove(temp_hocr)
            except Exception:
                pass


def process_all_versions(file_path: str, output_dir: str = None) -> dict:
    """
    Processes a given input image through the entire pipeline:
    - Normalization
    - Script-based cleaning
    - Doxa binarization (su, sauvola, wolf)
    - Tesseract OCR on all the versions
    
    Args:
        file_path (str): The path to the uploaded document image.
        output_dir (str, optional): The directory where output products should
            be stored. Defaults to same directory as file_path.

    Returns:
        dict: Mapped string paths of all generated PNGs and HTML hOCR products.
    """
    if not output_dir:
        output_dir = os.path.dirname(os.path.abspath(file_path))

    os.makedirs(output_dir, exist_ok=True)

    # 1. Normalize
    normed_path = os.path.join(output_dir, "original.png")
    normalize_image(file_path, normed_path, delete_source_if_different=True)

    # 2. Clean image with script
    cleaned_path = os.path.join(output_dir, "cleaned.png")
    clean_image_with_script(normed_path, cleaned_path)

    # 3. Doxa binarization
    doxa_algos = ["su", "sauvola", "wolf"]
    doxa_paths = {}
    for algo in doxa_algos:
        doxa_path = os.path.join(output_dir, f"doxa_{algo}.png")
        run_doxa_binarization(normed_path, doxa_path, algo)
        doxa_paths[algo] = doxa_path

    # 4. Run Tesseract OCR on all versions
    # Original
    original_html = os.path.join(output_dir, "original.html")
    run_tesseract_ocr(normed_path, original_html, "original.png")

    # Cleaned
    cleaned_html = os.path.join(output_dir, "cleaned.html")
    run_tesseract_ocr(cleaned_path, cleaned_html, "cleaned.png")

    # Doxa
    doxa_html_paths = {}
    for algo in doxa_algos:
        doxa_html = os.path.join(output_dir, f"doxa_{algo}.html")
        run_tesseract_ocr(doxa_paths[algo], doxa_html, f"doxa_{algo}.png")
        doxa_html_paths[algo] = doxa_html

    # Build result dictionary
    result = {
        "original_png": normed_path,
        "cleaned_png": cleaned_path,
        "doxa_su_png": doxa_paths["su"],
        "doxa_sauvola_png": doxa_paths["sauvola"],
        "doxa_wolf_png": doxa_paths["wolf"],
        "original_html": original_html,
        "cleaned_html": cleaned_html,
        "doxa_su_html": doxa_html_paths["su"],
        "doxa_sauvola_html": doxa_html_paths["sauvola"],
        "doxa_wolf_html": doxa_html_paths["wolf"],
    }
    return result


def process_file(file_path: str, project_root: str = None, file_id: str = None):
    """
    Main entry point for web app uploads.
    Handles errors and returns None on success, or (error_msg, status_code) on failure.

    Args:
        file_path (str): Path of the file to process.
        project_root (str, optional): Root folder of the project. Defaults to None.
        file_id (str, optional): Unique upload identifier. Defaults to None.

    Returns:
        None | tuple: None on successful execution, or a tuple (error_message, status_code) on error.
    """
    try:
        process_all_versions(file_path)
        return None
    except Exception as e:
        return str(e), 500

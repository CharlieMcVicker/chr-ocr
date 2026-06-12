#!/usr/bin/env python
"""
This module classifies detected layout columns / bounding boxes in images using Tesseract
OCR (with both Cherokee and English languages loaded) and analyzes character proportions
to categorize sections as Cherokee, English, Mixed, or Empty.
"""
import argparse
import sys
import os
import json
import csv
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import extract_columns, crop_pad_skew_correct
from server.process_file import ocr_image_to_text


def is_cherokee_char(c: str) -> bool:
    """
    Checks if a given character is within the Cherokee Unicode blocks.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if the character is Cherokee, False otherwise.
    """
    o = ord(c)
    # Cherokee: U+13A0 to U+13FF, Cherokee Supplement: U+AB70 to U+ABBF
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)


def is_latin_char(c: str) -> bool:
    """
    Checks if a given character is a Latin alphabet letter.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if the character is a Latin letter, False otherwise.
    """
    return c.isascii() and c.isalpha()


def analyze_text(text: str) -> dict:
    """
    Analyzes OCR string text to determine Cherokee vs Latin characters,
    calculates proportions, and classifies the dominant language.
    
    Args:
        text: String of OCR-extracted text.
        
    Returns:
        Dict containing counts, calculated classification, and stripped text.
    """
    cherokee_count = 0
    latin_count = 0
    for c in text:
        if is_cherokee_char(c):
            cherokee_count += 1
        elif is_latin_char(c):
            latin_count += 1

    total = cherokee_count + latin_count
    pct_cherokee = cherokee_count / total if total else 0

    if total == 0:
        classification = "Empty"
    elif pct_cherokee < 0.40:
        classification = "English"
    elif pct_cherokee > 0.45:
        classification = "Cherokee"
    else:
        classification = "Mixed"

    return {
        "cherokee_count": cherokee_count,
        "latin_count": latin_count,
        "classification": classification,
        "text": text.strip(),
    }


def main():
    """
    Main command-line entry point to parse scan image files in a folder,
    extract bounding boxes (or whole images), perform OCR, classify the text,
    and output CSV/JSON analysis reports.
    """
    parser = argparse.ArgumentParser(
        description="Classify layout bounding boxes using Tesseract Cherokee and English models."
    )
    parser.add_argument(
        "input_folder", help="Path to the folder containing image files"
    )
    parser.add_argument(
        "--output-dir",
        default="classification_results",
        help="Directory to save classification reports and cropped images",
    )
    parser.add_argument(
        "--direct-crops",
        action="store_true",
        help="If set, skip layout extraction and classify the entire input images directly",
    )
    parser.add_argument(
        "--save-crops",
        action="store_true",
        help="If set, save cropped bounding box images organized by predicted class",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=20,
        help="Margin in pixels to add around bounding boxes during cropping",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input_folder):
        print(
            f"Error: '{args.input_folder}' is not a valid directory.", file=sys.stderr
        )
        sys.exit(1)

    # Find supported images
    supported_extensions = (".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".jp2")
    image_files = [
        f
        for f in os.listdir(args.input_folder)
        if f.lower().endswith(supported_extensions)
    ]

    if not image_files:
        print(f"No images found in '{args.input_folder}'.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(image_files)} images in '{args.input_folder}'.")
    os.makedirs(args.output_dir, exist_ok=True)

    results = []

    # Loop through each image
    for img_name in sorted(image_files):
        img_path = os.path.join(args.input_folder, img_name)
        print(f"\nProcessing image: {img_name}")

        try:
            pil_img = Image.open(img_path).convert("RGB")
        except Exception as e:
            print(f"Failed to open image {img_name}: {e}", file=sys.stderr)
            continue

        if args.direct_crops:
            # Skip layout extraction, treat the whole image as the crop
            ocr_text = ocr_image_to_text(pil_img, lang="chr+eng")
            analysis = analyze_text(ocr_text)

            box_result = {
                "image_name": img_name,
                "box_index": 0,
                "bbox": [0, 0, pil_img.width, pil_img.height],
                "cherokee_count": analysis["cherokee_count"],
                "latin_count": analysis["latin_count"],
                "classification": analysis["classification"],
                "text": analysis["text"],
            }
            results.append(box_result)

            print(
                f"  -> Classification: {analysis['classification']} "
                f"(Cherokee: {analysis['cherokee_count']}, Latin: {analysis['latin_count']})"
            )

            # Optionally save crop
            if args.save_crops:
                classification = analysis["classification"].lower()
                class_dir = os.path.join(args.output_dir, f"{classification}_crops")
                os.makedirs(class_dir, exist_ok=True)
                pil_img.save(os.path.join(class_dir, img_name))
        else:
            # Extract bounding boxes
            print("  Extracting bounding boxes...")
            try:
                blocks = extract_columns(pil_img)
            except Exception as e:
                print(f"  Layout detection failed for {img_name}: {e}", file=sys.stderr)
                continue

            print(f"  Detected {len(blocks)} bounding boxes.")

            for idx, block in enumerate(blocks):
                bbox = block["bbox"]
                print(f"  Classifying box {idx:03d} {bbox}...")

                # Crop and skew correct
                try:
                    cropped = crop_pad_skew_correct(
                        pil_img, bbox, args.margin, args.margin
                    )
                except Exception as e:
                    print(
                        f"    Failed to crop/skew-correct box {idx:03d}: {e}",
                        file=sys.stderr,
                    )
                    continue

                # Run Tesseract OCR (chr+eng)
                ocr_text = ocr_image_to_text(cropped, lang="chr+eng")
                analysis = analyze_text(ocr_text)

                box_result = {
                    "image_name": img_name,
                    "box_index": idx,
                    "bbox": bbox,
                    "cherokee_count": analysis["cherokee_count"],
                    "latin_count": analysis["latin_count"],
                    "classification": analysis["classification"],
                    "text": analysis["text"],
                }
                results.append(box_result)

                print(
                    f"    -> Classification: {analysis['classification']} "
                    f"(Cherokee: {analysis['cherokee_count']}, Latin: {analysis['latin_count']})"
                )

                # Optionally save crop
                if args.save_crops:
                    classification = analysis["classification"].lower()
                    class_dir = os.path.join(args.output_dir, f"{classification}_crops")
                    os.makedirs(class_dir, exist_ok=True)
                    crop_filename = f"{os.path.splitext(img_name)[0]}_box_{idx:03d}.png"
                    cropped.save(os.path.join(class_dir, crop_filename))

    # Save reports
    report_json_path = os.path.join(args.output_dir, "classification_report.json")
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    report_csv_path = os.path.join(args.output_dir, "classification_report.csv")
    with open(report_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_name",
                "box_index",
                "bbox",
                "cherokee_count",
                "latin_count",
                "classification",
                "text",
            ],
        )
        writer.writeheader()
        for r in results:
            # format bbox for CSV readability
            r_copy = r.copy()
            r_copy["bbox"] = ",".join(map(str, r_copy["bbox"]))
            writer.writerow(r_copy)

    print(f"\nClassification complete. Results saved to '{args.output_dir}':")
    print(f"  - JSON report: {report_json_path}")
    print(f"  - CSV report: {report_csv_path}")


if __name__ == "__main__":
    main()

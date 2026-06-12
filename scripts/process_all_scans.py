#!/usr/bin/env python3
"""
This module processes all page scan files in a folder recursively,
extracts layout columns, runs Tesseract OCR to classify layout blocks,
and saves the cropped, skew-corrected slices categorized under Cherokee,
English, or Other directories.
"""
import os
import sys
import argparse
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import extract_columns, crop_pad_skew_correct
from server.process_file import ocr_image_to_text
from scripts.classify_layout import analyze_text

def find_scans(base_dir):
    """
    Searches recursively under a directory for supported page scans.
    
    Args:
        base_dir: Root directory path to search.
        
    Returns:
        Sorted list of scan image paths.
    """
    supported = (".jp2", ".png", ".jpg", ".jpeg", ".tiff", ".bmp")
    scan_files = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(supported):
                scan_files.append(os.path.join(root, f))
    return sorted(scan_files)

def process_scans(input_dir, output_dir, margin=20, skip_existing=True):
    """
    Processes all found scan files: extracts columns, crop/skew-corrects them,
    classifies their language, and saves the categorized column crops.
    
    Args:
        input_dir: Source scans directory.
        output_dir: Destination results directory.
        margin: Crop padding margin.
        skip_existing: Boolean to skip already-cropped slices.
    """
    scans = find_scans(input_dir)
    print(f"Found {len(scans)} scan images in '{input_dir}' recursively.")
    
    cherokee_dir = os.path.join(output_dir, "cherokee_crops")
    english_dir = os.path.join(output_dir, "english_crops")
    other_dir = os.path.join(output_dir, "other_crops")
    
    os.makedirs(cherokee_dir, exist_ok=True)
    os.makedirs(english_dir, exist_ok=True)
    os.makedirs(other_dir, exist_ok=True)
    
    for i, scan_path in enumerate(scans, 1):
        # Create a clean unique identifier prefix based on directory structure relative to input_dir
        rel_path = os.path.relpath(scan_path, input_dir)
        path_parts = rel_path.replace(os.sep, "_")
        prefix = os.path.splitext(path_parts)[0]
        
        print(f"\n[{i}/{len(scans)}] Processing: {rel_path}")
        
        try:
            pil_img = Image.open(scan_path).convert("RGB")
        except Exception as e:
            print(f"  Failed to open image: {e}", file=sys.stderr)
            continue
            
        # Extract columns
        try:
            blocks = extract_columns(pil_img)
            print(f"  Detected {len(blocks)} bounding boxes.")
        except Exception as e:
            print(f"  Layout detection failed: {e}", file=sys.stderr)
            continue
            
        for idx, block in enumerate(blocks):
            bbox = block["bbox"]
            crop_filename = f"{prefix}_box_{idx:03d}.png"
            
            # Determine target paths
            c_path = os.path.join(cherokee_dir, crop_filename)
            e_path = os.path.join(english_dir, crop_filename)
            o_path = os.path.join(other_dir, crop_filename)
            
            # Check if we should skip
            if skip_existing and (os.path.exists(c_path) or os.path.exists(e_path) or os.path.exists(o_path)):
                print(f"  Box {idx:03d}: [Skipped] Already processed/exists")
                continue
                
            print(f"  Classifying box {idx:03d} {bbox}...")
            
            # Crop & skew correct
            try:
                cropped = crop_pad_skew_correct(pil_img, bbox, margin, margin)
            except Exception as e:
                print(f"    Failed to crop/skew-correct box {idx:03d}: {e}", file=sys.stderr)
                continue
                
            # OCR & Classify
            try:
                ocr_text = ocr_image_to_text(cropped, lang="chr+eng")
                analysis = analyze_text(ocr_text)
                classification = analysis["classification"].lower()
            except Exception as e:
                print(f"    OCR / classification failed: {e}", file=sys.stderr)
                continue
                
            # Save to correct folder
            if classification == "cherokee":
                dest = c_path
            elif classification == "english":
                dest = e_path
            else:
                dest = o_path
                
            try:
                cropped.save(dest)
                print(f"    -> Saved as {classification.capitalize()} crop to {os.path.basename(dest)}")
            except Exception as e:
                print(f"    Failed to save crop: {e}", file=sys.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively process all scans, crop, classify, and sort into cherokee and english folders.")
    parser.add_argument("--input-dir", default="scans", help="Base directory containing scan files")
    parser.add_argument("--output-dir", default="all_results", help="Directory where output folders will be created")
    parser.add_argument("--margin", type=int, default=20, help="Margin around bounding box crop")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing crop files instead of skipping them")
    
    args = parser.parse_args()
    
    process_scans(args.input_dir, args.output_dir, margin=args.margin, skip_existing=not args.overwrite)

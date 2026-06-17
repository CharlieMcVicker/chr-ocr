#!/usr/bin/env python3
"""
package_cnt_test_data.py

Processes the aligned manifest for Cherokee New Testament (CNT) Book 01,
copies the cropped line PNGs to training_data/dataset/test/cnt/,
height-normalizes them, generates the corresponding .gt.txt and .box files,
and compiles them into .lstmf files using tesseract.
"""

import os
import sys
import json
import shutil
import cv2
import subprocess
from concurrent.futures import ThreadPoolExecutor

def normalize_height(image, target_line_height=42, pad_y=3):
    img_height, img_width = image.shape[:2]
    if img_height == 0 or img_width == 0:
        return image
    line_height = max(1, img_height - 2 * pad_y)
    ratio = target_line_height / float(line_height)
    target_height = int(round(ratio * img_height))
    target_width = int(round(ratio * img_width))
    if target_width == 0: target_width = 1
    if target_height == 0: target_height = 1
    resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return resized

def generate_box_file(box_path, text, width, height):
    with open(box_path, "w", encoding="utf-8") as f:
        f.write(f"WordStr 0 0 {width} {height} 0 #{text}\n")
        f.write(f"\t 0 0 {width} {height} 0\n")

def main():
    aligned_manifest_path = "training_data/cnt/book_01/aligned_manifest.json"
    book_dir = "training_data/cnt/book_01"
    
    # Destination directory for test dataset
    dest_dir = "training_data/dataset/test/cnt"
    os.makedirs(dest_dir, exist_ok=True)
    
    if not os.path.exists(aligned_manifest_path):
        print(f"Error: {aligned_manifest_path} not found.")
        sys.exit(1)
        
    print(f"Loading aligned manifest from {aligned_manifest_path}...")
    with open(aligned_manifest_path, "r", encoding="utf-8") as f:
        aligned_data = json.load(f)
        
    # We will gather all lines to compile
    lines_to_process = []
    
    # Traverse aligned_manifest
    for verse_key, info in aligned_data.items():
        for line_idx, line in enumerate(info["lines"]):
            # Get the aligned ground truth text from the fine-tuned aligned OCR mapping
            gt_text = line.get("ftm_aligned", "").strip()
            if not gt_text:
                continue
                
            crop_rel_path = line["line_crop"]
            crop_abs_path = os.path.join(book_dir, crop_rel_path)
            
            if not os.path.exists(crop_abs_path):
                print(f"Warning: Crop image {crop_abs_path} does not exist.")
                continue
                
            # Load image and height normalize
            img = cv2.imread(crop_abs_path)
            if img is None:
                continue
            norm_img = normalize_height(img, target_line_height=42, pad_y=3)
            h, w = norm_img.shape[:2]
            
            # Construct a clean filename for destination
            # Format: cnt_book_01_verse_{verse_key}_line_{line_idx:02d}
            base_name = f"cnt_01_{verse_key}_line_{line_idx:02d}"
            
            dest_png = os.path.join(dest_dir, f"{base_name}.png")
            dest_gt = os.path.join(dest_dir, f"{base_name}.gt.txt")
            dest_box = os.path.join(dest_dir, f"{base_name}.box")
            
            # Write PNG
            cv2.imwrite(dest_png, norm_img)
            
            # Write GT text
            with open(dest_gt, "w", encoding="utf-8") as gt_f:
                gt_f.write(gt_text + "\n")
                
            # Write Box file
            generate_box_file(dest_box, gt_text, w, h)
                
            lines_to_process.append((dest_png, dest_gt, base_name))
            
    print(f"Copied, normalized and prepared {len(lines_to_process)} crops to {dest_dir}.")
    
    # Compile PNGs to .lstmf files
    system_tessdata = "/opt/homebrew/share/tessdata"
    
    # We will use the workspace folder containing chr_best_finetuned.traineddata
    workspace_dir = "/Users/charlesmcvicker/.gemini/antigravity/worktrees/phoenix/spike-scrape-cherokee-testament"
    
    def compile_png(item):
        png_path, gt_path, base = item
        base_path = os.path.join(dest_dir, base)
        lstmf_path = base_path + ".lstmf"
        
        # Remove old lstmf if exists
        if os.path.exists(lstmf_path):
            os.remove(lstmf_path)
            
        subprocess.run([
            "tesseract",
            png_path,
            base_path,
            "--tessdata-dir", workspace_dir,
            "-l", "chr_best_finetuned",
            "--oem", "1",
            "--psm", "13",
            f"{system_tessdata}/configs/lstm.train"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return lstmf_path

    print(f"Compiling {len(lines_to_process)} images to .lstmf using {workspace_dir} and chr_best_finetuned.traineddata...")
    
    # Compile
    with ThreadPoolExecutor() as executor:
        lstmf_files = list(executor.map(compile_png, lines_to_process))
        
    # Write list.test
    list_file = os.path.join(dest_dir, "list.test")
    with open(list_file, "w", encoding="utf-8") as lf:
        for lp in lstmf_files:
            lf.write(os.path.abspath(lp) + "\n")
            
    print(f"Generated list.test containing {len(lstmf_files)} entries at {list_file}")

if __name__ == "__main__":
    main()

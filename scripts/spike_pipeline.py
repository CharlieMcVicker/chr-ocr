#!/usr/bin/env python3
import os
import json
import subprocess
import cv2
import numpy as np

def augment_image(image):
    # Basic augmentation for spike: slight rotation and Otsu thresholding
    height, width = image.shape[:2]
    
    # Rotate 1 degree
    center = (width / 2, height / 2)
    M = cv2.getRotationMatrix2D(center, 1.0, 1.0)
    rotated = cv2.warpAffine(image, M, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    # Convert to grayscale
    gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)
    
    # Otsu Binarization
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh

def normalize_height(image, target_height=48):
    # Tesseract typically expects 48px height for LSTM training
    h, w = image.shape[:2]
    ratio = target_height / float(h)
    new_width = int(w * ratio)
    resized = cv2.resize(image, (new_width, target_height), interpolation=cv2.INTER_AREA)
    return resized

def generate_box_file(box_path, text, width, height):
    # WordStr box file format for Tesseract LSTM training
    with open(box_path, "w", encoding="utf-8") as f:
        # Tesseract expects WordStr format for line images
        f.write(f"WordStr 0 0 {width} {height} 0 #{text}\n")
        f.write(f"\t 0 0 {width} {height} 0\n")

def main():
    manifest_path = "training_data_v2/manifest.json"
    output_dir = "dataset/train"
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(manifest_path):
        print(f"Manifest not found: {manifest_path}")
        return
        
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    labeled_count = 0
    lstmf_paths = []
    
    for item in manifest.values():
        if item.get("status") == "labeled":
            labeled_count += 1
            image_path = os.path.join("training_data_v2", item["image_path"])
            label = item["label"]
            item_id = item["id"]
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Failed to read image {image_path}")
                continue
                
            # Augment & Normalize
            aug_img = augment_image(img)
            norm_img = normalize_height(aug_img, target_height=48)
            h, w = norm_img.shape[:2]
            
            # Paths
            base_path = os.path.join(output_dir, item_id)
            png_path = f"{base_path}.png"
            gt_path = f"{base_path}.gt.txt"
            box_path = f"{base_path}.box"
            
            # Save files
            cv2.imwrite(png_path, norm_img)
            
            with open(gt_path, "w", encoding="utf-8") as f:
                f.write(label + "\n")
                
            generate_box_file(box_path, label, w, h)
            
            # Run tesseract to generate .lstmf
            cmd = [
                "tesseract",
                png_path,
                base_path,
                "-l", "chr",
                "--psm", "13",
                "lstm.train"
            ]
            print(f"Running tesseract for {item_id}...")
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                print(f"Tesseract failed for {item_id}: {res.stderr}")
            else:
                lstmf_paths.append(f"{base_path}.lstmf")
                
    if labeled_count == 0:
        print("No labeled items found in manifest. Please label some items first.")
        return
        
    # Generate list.train
    list_train_path = os.path.join(output_dir, "list.train")
    with open(list_train_path, "w", encoding="utf-8") as f:
        for path in lstmf_paths:
            f.write(os.path.abspath(path) + "\n")
            
    print(f"\nPipeline complete! Generated {len(lstmf_paths)} .lstmf files.")
    print(f"list.train written to {list_train_path}")

if __name__ == "__main__":
    main()

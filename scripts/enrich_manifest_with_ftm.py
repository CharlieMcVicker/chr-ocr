#!/usr/bin/env python3
"""
This module enriches the existing `manifest_w_lang.json` manifest with OCR transcriptions
and word-level confidence scores produced by the best fine-tuned Cherokee Tesseract LSTM model.
It gathers performance statistics to identify low-confidence predictions for targeted review.
"""
import os
import sys
import json
import argparse
from PIL import Image
import pytesseract

def main():
    """
    Main entry point to read the manifest, execute PyTesseract OCR on each image
    using the fine-tuned traineddata, compute mean confidence, write progress,
    and generate summary statistics and a low-confidence list.
    """
    parser = argparse.ArgumentParser(description="Enrich manifest with FTM predictions")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force regeneration of all predictions even if they already exist"
    )
    args = parser.parse_args()

    base_dir = "training_data_v2"
    manifest_path = os.path.join(base_dir, "manifest_w_lang.json")
    
    if not os.path.exists(manifest_path):
        print(f"Error: Could not find {manifest_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading {manifest_path}...")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    model_dir = "/Users/charlesmcvicker/code/phoenix/training_data_v2/dataset/model"
    model_name = "chr_best_finetuned"
    traineddata_path = os.path.join(model_dir, f"{model_name}.traineddata")
    
    if not os.path.exists(traineddata_path):
        print(f"Error: Could not find fine-tuned model at {traineddata_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Using fine-tuned model: {traineddata_path}")
    
    config = f"--tessdata-dir {model_dir} --psm 7"
    
    total = len(manifest)
    processed = 0
    skipped = 0
    updated_since_last_save = 0
    save_interval = 100
    
    for idx, (key, item) in enumerate(manifest.items()):
        if not args.force and 'ftm_ocr' in item and 'ftm_confidence' in item:
            if item['ftm_ocr'] != "Error":
                skipped += 1
                continue
            
        img_path = os.path.join(base_dir, item['image_path'])
        
        if not os.path.exists(img_path):
            fallback_path = os.path.join("training_data", item['image_path'])
            if os.path.exists(fallback_path):
                img_path = fallback_path
        
        try:
            # Open image and convert to RGB
            with Image.open(img_path) as pil_img:
                pil_img = pil_img.convert("RGB")
                
                # Run OCR with pytesseract image_to_data to get word-level confidences
                data = pytesseract.image_to_data(
                    pil_img, 
                    lang=model_name, 
                    config=config, 
                    output_type=pytesseract.Output.DICT
                )
                
                # Reconstruct OCR string from words
                words = [w for w in data['text'] if w.strip()]
                ocr_text = ' '.join(words)
                
                # Filter out -1 confidences (used for block/para/line indicators)
                confs = [c for c in data['conf'] if c != -1]
                
                # Calculate mean confidence for the line
                if confs:
                    mean_conf = sum(confs) / len(confs)
                else:
                    mean_conf = 0.0
                    
                item['ftm_ocr'] = ocr_text
                item['ftm_confidence'] = round(mean_conf, 2)
                
            processed += 1
            updated_since_last_save += 1
            
            if processed % 10 == 0 or processed == 1:
                print(f"[{skipped + processed}/{total}] Enriched {item['image_path']}: conf={item['ftm_confidence']}, ocr={repr(ocr_text)}")
                
        except Exception as e:
            print(f"[{skipped + processed}/{total}] Error enriching {item['image_path']}: {e}", file=sys.stderr)
            item['ftm_ocr'] = "Error"
            item['ftm_confidence'] = 0.0
            processed += 1
            updated_since_last_save += 1
            
        if updated_since_last_save >= save_interval:
            print(f"Saving progress to {manifest_path}...")
            temp_path = manifest_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, manifest_path)
            updated_since_last_save = 0
            
    # Final save
    if updated_since_last_save > 0 or processed == total:
        print(f"Saving final manifest to {manifest_path}...")
        temp_path = manifest_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, manifest_path)
        
    print(f"\nProcessing Complete!")
    print(f"Total entries in manifest: {total}")
    print(f"Skipped (already enriched): {skipped}")
    print(f"Newly processed: {processed}")
    
    # Generate statistics across all successfully processed items
    valid_confs = []
    errors_count = 0
    for key, item in manifest.items():
        conf = item.get('ftm_confidence')
        if conf is not None:
            if item.get('ftm_ocr') == "Error":
                errors_count += 1
            else:
                valid_confs.append(conf)
                
    if valid_confs:
        valid_confs.sort()
        n = len(valid_confs)
        p10 = valid_confs[int(n * 0.10)]
        p25 = valid_confs[int(n * 0.25)]
        p50 = valid_confs[int(n * 0.50)]
        p75 = valid_confs[int(n * 0.75)]
        mean_c = sum(valid_confs) / n
        print(f"\nConfidence Score Statistics:")
        print(f"  Mean Confidence: {mean_c:.2f}%")
        print(f"  Percentiles:")
        print(f"    10th percentile: {p10:.2f}%")
        print(f"    25th percentile: {p25:.2f}%")
        print(f"    50th percentile (Median): {p50:.2f}%")
        print(f"    75th percentile: {p75:.2f}%")
        print(f"  OCR Errors encountered: {errors_count}")
        
        # Print the lowest confidence items
        print("\nTop 20 Lowest Confidence Entries (for targeted hand-labeling):")
        lowest_items = []
        for key, item in manifest.items():
            if item.get('ftm_ocr') != "Error" and 'ftm_confidence' in item:
                lowest_items.append((key, item['ftm_confidence'], item['image_path'], item['ftm_ocr']))
        lowest_items.sort(key=lambda x: x[1])
        for idx, (k, c, path, ocr) in enumerate(lowest_items[:20]):
            print(f"  {idx+1:2d}. ID: {k} | Conf: {c:5.2f}% | Path: {path} | OCR: {repr(ocr)}")
            
if __name__ == "__main__":
    main()

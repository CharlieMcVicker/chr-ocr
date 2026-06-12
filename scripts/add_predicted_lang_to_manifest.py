#!/usr/bin/env python3
"""
This module processes a training dataset manifest and enriches it by predicting
the language (Cherokee, English, or Mix) of each image using OCR and text classification.
It updates or creates an enriched manifest `manifest_w_lang.json` while allowing
for process resumption.
"""
import os
import sys
import json
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.process_file import ocr_image_to_text
from scripts.classify_layout import analyze_text

def main():
    """
    Main function to load the dataset manifest, run OCR on each image,
    classify its language, and save the enriched data to `manifest_w_lang.json`.
    """
    base_dir = "training_data_v2"
    manifest_path = os.path.join(base_dir, "manifest.json")
    out_manifest_path = os.path.join(base_dir, "manifest_w_lang.json")
    
    if not os.path.exists(manifest_path):
        print(f"Error: Could not find {manifest_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Loading {manifest_path}...")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
        
    out_manifest = {}
    if os.path.exists(out_manifest_path):
        print(f"Loading existing {out_manifest_path} to resume...")
        try:
            with open(out_manifest_path, 'r', encoding='utf-8') as f:
                out_manifest = json.load(f)
        except Exception as e:
            print(f"Warning: could not load existing {out_manifest_path}: {e}")
            
    # Merge existing base manifest into out_manifest (without overwriting existing predicted_lang)
    for k, v in manifest.items():
        if k not in out_manifest:
            out_manifest[k] = v.copy()
        else:
            # ensure any base updates are merged but we keep our predicted_lang if we have it
            if 'predicted_lang' in out_manifest[k]:
                lang = out_manifest[k]['predicted_lang']
                out_manifest[k].update(v)
                out_manifest[k]['predicted_lang'] = lang
            else:
                out_manifest[k] = v.copy()

    total = len(out_manifest)
    processed = 0
    updated_since_last_save = 0
    save_interval = 50
    
    for idx, (key, item) in enumerate(out_manifest.items()):
        if 'predicted_lang' in item:
            processed += 1
            continue
            
        img_path = os.path.join(base_dir, item['image_path'])
        
        try:
            pil_img = Image.open(img_path).convert("RGB")
            # Run OCR
            ocr_text = ocr_image_to_text(pil_img, lang="chr+eng")
            analysis = analyze_text(ocr_text)
            
            item['predicted_lang'] = analysis["classification"]
            
            # Print progress nicely
            print(f"[{processed+1}/{total}] Classifying {item['image_path']}: {analysis['classification']}")
            
        except Exception as e:
            print(f"[{processed+1}/{total}] Error classifying {item['image_path']}: {e}", file=sys.stderr)
            item['predicted_lang'] = "Error"
            
        processed += 1
        updated_since_last_save += 1
        
        if updated_since_last_save >= save_interval:
            print(f"Saving progress to {out_manifest_path}...")
            # Save to a temp file and rename to avoid corruption
            temp_path = out_manifest_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(out_manifest, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, out_manifest_path)
            updated_since_last_save = 0
            
    # Final save
    if updated_since_last_save > 0 or processed == total:
        print(f"Saving final manifest to {out_manifest_path}...")
        temp_path = out_manifest_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(out_manifest, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, out_manifest_path)
        
    print("Done!")

if __name__ == "__main__":
    main()

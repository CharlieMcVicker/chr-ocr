"""
This module contains functions to enrich manifests with OCR predictions using fine-tuned models
and classifying lines to add language predictions.
"""

import os
import sys
import json
from PIL import Image
import pytesseract
from phoenix.layout.classification import classify_line_image

def enrich_manifest_with_ftm(
    manifest_path: str,
    model_dir: str = "/Users/charlesmcvicker/code/phoenix/training_data/dataset/model",
    model_name: str = "chr_best_finetuned",
    base_dir: str = "training_data",
    force: bool = False,
    save_interval: int = 100
):
    """
    Reads the manifest, executes PyTesseract OCR on each image using the fine-tuned model,
    calculates mean word confidence, and writes progress to the manifest file.
    """
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Could not find manifest at: {manifest_path}")

    print(f"Loading {manifest_path}...")
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    traineddata_path = os.path.join(model_dir, f"{model_name}.traineddata")
    if not os.path.exists(traineddata_path):
        raise FileNotFoundError(f"Could not find fine-tuned model at {traineddata_path}")

    print(f"Using fine-tuned model: {traineddata_path}")
    config = f"--tessdata-dir {model_dir} --psm 7"

    total = len(manifest)
    processed = 0
    skipped = 0
    updated_since_last_save = 0

    for idx, (key, item) in enumerate(manifest.items()):
        if not force and 'ftm_ocr' in item and 'ftm_confidence' in item:
            if item['ftm_ocr'] != "Error":
                skipped += 1
                continue

        img_path = os.path.join(base_dir, item['image_path'])
        if not os.path.exists(img_path):
            fallback_path = os.path.join("training_data", item['image_path'])
            if os.path.exists(fallback_path):
                img_path = fallback_path

        try:
            with Image.open(img_path) as pil_img:
                pil_img = pil_img.convert("RGB")
                data = pytesseract.image_to_data(
                    pil_img,
                    lang=model_name,
                    config=config,
                    output_type=pytesseract.Output.DICT
                )
                words = [w for w in data['text'] if w.strip()]
                ocr_text = ' '.join(words)
                confs = [c for c in data['conf'] if c != -1]
                mean_conf = sum(confs) / len(confs) if confs else 0.0

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

def add_predicted_lang_to_manifest(
    manifest_path: str,
    out_manifest_path: str,
    base_dir: str = "training_data",
    save_interval: int = 50
):
    """
    Loads base manifest, predicts language classification for each image,
    and saves the enriched data.
    """
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Could not find manifest at: {manifest_path}")

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

    # Merge base manifest into out_manifest (without overwriting existing predicted_lang)
    for k, v in manifest.items():
        if k not in out_manifest:
            out_manifest[k] = v.copy()
        else:
            if 'predicted_lang' in out_manifest[k]:
                lang = out_manifest[k]['predicted_lang']
                out_manifest[k].update(v)
                out_manifest[k]['predicted_lang'] = lang
            else:
                out_manifest[k] = v.copy()

    total = len(out_manifest)
    processed = 0
    updated_since_last_save = 0

    for idx, (key, item) in enumerate(out_manifest.items()):
        if 'predicted_lang' in item:
            processed += 1
            continue

        img_path = os.path.join(base_dir, item['image_path'])
        try:
            pil_img = Image.open(img_path).convert("RGB")
            classification = classify_line_image(pil_img)
            item['predicted_lang'] = classification
            print(f"[{processed+1}/{total}] Classifying {item['image_path']}: {classification}")
        except Exception as e:
            print(f"[{processed+1}/{total}] Error classifying {item['image_path']}: {e}", file=sys.stderr)
            item['predicted_lang'] = "Error"

        processed += 1
        updated_since_last_save += 1

        if updated_since_last_save >= save_interval:
            print(f"Saving progress to {out_manifest_path}...")
            temp_path = out_manifest_path + ".tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(out_manifest, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, out_manifest_path)
            updated_since_last_save = 0

    if updated_since_last_save > 0 or processed == total:
        print(f"Saving final manifest to {out_manifest_path}...")
        temp_path = out_manifest_path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(out_manifest, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, out_manifest_path)

    print("Done!")

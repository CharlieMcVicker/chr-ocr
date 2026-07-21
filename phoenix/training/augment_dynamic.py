#!/usr/bin/env python3
"""
This module implements advanced dynamic data augmentation for the Cherokee OCR dataset.
It integrates Albumentations to apply sensor noise, spatial distortions, occlusion techniques,
and weakly-supervised synthetic error injection on the training set.
"""
import os
import json
import random
import cv2
import numpy as np
import argparse
import sys
from PIL import Image


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phoenix.training.augment import (
    normalize_height,
    generate_box_file,
    inject_synthetic_errors,
    binarize,
    get_albumentations_pipeline,
    apply_mixup_bleedthrough,
    apply_ink_wash_smudge
)
from phoenix.text.normalization import normalize_truth

def compile_image(img_path, model_dir):
    """
    Compiles a single PNG image to .lstmf using tesseract.
    """
    import subprocess
    import glob
    base = os.path.splitext(img_path)[0]
    # Find the correct path of lstm.train inside homebrew directory
    lstm_train_config = "/opt/homebrew/share/tessdata/configs/lstm.train"
    if not os.path.exists(lstm_train_config):
        # fallback to Cellar path
        matches = glob.glob("/opt/homebrew/Cellar/tesseract/*/share/tessdata/configs/lstm.train")
        if matches:
            lstm_train_config = matches[0]

    subprocess.run(
        ["tesseract", img_path, base, "--tessdata-dir", model_dir, "-l", "chr", "--oem", "1", "--psm", "13", lstm_train_config],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )
    return os.path.abspath(base + ".lstmf")

def generate_variations_worker(item, train_img_paths, args, rare_chars):
    """
    Worker function to process a single item's variations.
    Writes PNG, gt.txt, and box files to disk.
    Returns a list of metadata records.
    """
    cv2.setNumThreads(0)
    pipeline = get_albumentations_pipeline(
        blur_prob=args.blur_prob,
        shadow_prob=args.shadow_prob,
        distortion_prob=args.distortion_prob,
        dropout_prob=args.dropout_prob,
        distortion_limit=args.distortion_limit,
        elastic_alpha=args.elastic_alpha,
        elastic_sigma=args.elastic_sigma,
        use_multi_scale=args.use_multi_scale,
        page_curl_prob=args.page_curl_prob,
        page_curl_direction=args.page_curl_direction,
        page_curl_bending_factor=args.page_curl_bending_factor,
        page_curl_compression_factor=args.page_curl_compression_factor,
        page_curl_width_ratio=args.page_curl_width_ratio,
    )

    cnt_pipeline = get_albumentations_pipeline(
        blur_prob=args.cnt_blur_prob,
        shadow_prob=args.cnt_shadow_prob,
        distortion_prob=args.cnt_distortion_prob,
        dropout_prob=args.cnt_dropout_prob,
        blur_limit=(args.cnt_blur_limit_min, args.cnt_blur_limit_max),
        shadow_dimension=args.cnt_shadow_dimension,
        distortion_limit=args.cnt_distortion_limit,
        dropout_holes_range=(args.cnt_dropout_holes_min, args.cnt_dropout_holes_max),
        dropout_size_range=(args.cnt_dropout_size_min, args.cnt_dropout_size_max),
        micro_dropout_prob=args.cnt_micro_dropout_prob,
        micro_dropout_holes_range=(args.cnt_micro_dropout_holes_min, args.cnt_micro_dropout_holes_max),
        micro_dropout_size_range=(args.cnt_micro_dropout_size_min, args.cnt_micro_dropout_size_max),
        elastic_alpha=args.cnt_elastic_alpha,
        elastic_sigma=args.cnt_elastic_sigma,
        use_multi_scale=args.cnt_use_multi_scale,
        page_curl_prob=args.cnt_page_curl_prob,
        page_curl_direction=args.cnt_page_curl_direction,
        page_curl_bending_factor=args.cnt_page_curl_bending_factor,
        page_curl_compression_factor=args.cnt_page_curl_compression_factor,
        page_curl_width_ratio=args.cnt_page_curl_width_ratio,
    )

    bin_methods = ["otsu", "sauvola", "wolf", "grayscale"]

    image_path = os.path.join("training_data", item["image_path"])
    img = cv2.imread(image_path)
    if img is None:
        return []

    label = normalize_truth(item["label"])
    item_id = item["id"]

    skip_bin = (item.get("dataset") == "cnt")
    has_rare = any(c in label for c in rare_chars)
    variations = args.variations_per_image * 2 if has_rare else args.variations_per_image

    records = []
    for var_idx in range(variations):
        if skip_bin:
            augmented = cnt_pipeline(image=img)["image"]
            if random.random() < args.cnt_smudge_prob:
                augmented = apply_ink_wash_smudge(augmented, intensity=args.cnt_smudge_intensity)
            gray = cv2.cvtColor(augmented, cv2.COLOR_BGR2GRAY) if len(augmented.shape) == 3 else augmented
            bin_res = gray
            algo = "native"
        else:
            augmented = apply_mixup_bleedthrough(img, train_img_paths, p=args.bleedthrough_prob)
            augmented = pipeline(image=augmented)["image"]
            algo = random.choice(bin_methods)
            if algo == "otsu":
                bin_res = binarize(augmented, "otsu", {})
            elif algo == "sauvola":
                w = random.choice([15, 25, 35, 45])
                bin_res = binarize(augmented, "sauvola", {"window": w, "k": 0.1})
            elif algo == "wolf":
                w = random.choice([15, 25, 35, 45])
                k = random.choice([0.1, 0.2, 0.3])
                bin_res = binarize(augmented, "wolf", {"window": w, "k": k})
            elif algo == "grayscale":
                bin_res = cv2.cvtColor(augmented, cv2.COLOR_BGR2GRAY) if len(augmented.shape) == 3 else augmented

        norm_img = normalize_height(bin_res, pad_y=args.pad_y)
        h, w = norm_img.shape[:2]

        final_label = inject_synthetic_errors(label, error_rate=args.error_rate)
        normalized_final_label = normalize_truth(final_label)

        out_name = f"{item_id}_dyn_{var_idx}_{algo}"
        out_base = os.path.join(args.output_dir, out_name)

        pil_img = Image.fromarray(norm_img).convert('1')
        pil_img.save(out_base + ".tiff", compression="group4")
        with open(out_base + ".gt.txt", "w", encoding="utf-8") as f:
            f.write(normalized_final_label + "\n")
        generate_box_file(out_base + ".box", normalized_final_label, w, h)

        records.append({
            "id": item_id,
            "dataset": item.get("dataset", "phoenix"),
            "variation_id": out_name,
            "tiff_path": os.path.abspath(out_base + ".tiff"),
            "gt_path": os.path.abspath(out_base + ".gt.txt"),
            "box_path": os.path.abspath(out_base + ".box"),
            "lstmf_path": None,
            "label": normalized_final_label,
            "has_rare": has_rare,
            "algo": algo,
            "variation": var_idx,
            "error_rate": args.error_rate
        })
    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="training_data/manifest_w_lang.json")
    parser.add_argument("--output-dir", required=True, help="Directory to save augmented outputs")
    parser.add_argument("--split", type=float, default=0.8, help="Train split ratio")
    parser.add_argument("--pad-y", type=int, default=3, help="Y padding")
    parser.add_argument("--variations-per-image", type=int, default=3, help="Number of variations per image")
    parser.add_argument("--error-rate", type=float, default=0.05, help="Transcription error injection rate")
    parser.add_argument("--compile-lstmf", action="store_true", help="Compile generated TIFFs to .lstmf files")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Directory where chr.traineddata is located")
    parser.add_argument("--metadata-index", default=None, help="Path to write the metadata index JSON")
    
    # Augmentation options
    parser.add_argument("--blur-prob", type=float, default=0.5)
    parser.add_argument("--shadow-prob", type=float, default=0.4)
    parser.add_argument("--distortion-prob", type=float, default=0.45)
    parser.add_argument("--dropout-prob", type=float, default=0.4)
    parser.add_argument("--bleedthrough-prob", type=float, default=0.25)
    parser.add_argument("--distortion-limit", type=float, default=0.05)
    parser.add_argument("--elastic-alpha", type=float, default=1.0)
    parser.add_argument("--elastic-sigma", type=float, default=15.0)
    parser.add_argument("--use-multi-scale", type=lambda x: (str(x).lower() == "true"), default=False)
    
    # Page Curl options
    parser.add_argument("--page-curl-prob", type=float, default=0.0)
    parser.add_argument("--page-curl-direction", type=str, default="random")
    parser.add_argument("--page-curl-bending-factor", type=float, default=0.15)
    parser.add_argument("--page-curl-compression-factor", type=float, default=0.5)
    parser.add_argument("--page-curl-width-ratio", type=float, default=0.3)
    
    # CNT Augmentation options
    parser.add_argument("--cnt-blur-prob", type=float, default=0.6)
    parser.add_argument("--cnt-shadow-prob", type=float, default=0.5)
    parser.add_argument("--cnt-distortion-prob", type=float, default=0.5)
    parser.add_argument("--cnt-dropout-prob", type=float, default=0.5)
    parser.add_argument("--cnt-blur-limit-min", type=int, default=3)
    parser.add_argument("--cnt-blur-limit-max", type=int, default=5)
    parser.add_argument("--cnt-shadow-dimension", type=int, default=6)
    parser.add_argument("--cnt-distortion-limit", type=float, default=0.15)
    parser.add_argument("--cnt-dropout-holes-min", type=int, default=1)
    parser.add_argument("--cnt-dropout-holes-max", type=int, default=4)
    parser.add_argument("--cnt-dropout-size-min", type=int, default=4)
    parser.add_argument("--cnt-dropout-size-max", type=int, default=10)
    parser.add_argument("--cnt-micro-dropout-prob", type=float, default=0.4)
    parser.add_argument("--cnt-micro-dropout-holes-min", type=int, default=20)
    parser.add_argument("--cnt-micro-dropout-holes-max", type=int, default=60)
    parser.add_argument("--cnt-micro-dropout-size-min", type=int, default=1)
    parser.add_argument("--cnt-micro-dropout-size-max", type=int, default=2)
    parser.add_argument("--cnt-smudge-prob", type=float, default=0.4)
    parser.add_argument("--cnt-smudge-intensity", type=float, default=0.3)
    parser.add_argument("--cnt-elastic-alpha", type=float, default=1.0)
    parser.add_argument("--cnt-elastic-sigma", type=float, default=15.0)
    parser.add_argument("--cnt-use-multi-scale", type=lambda x: (str(x).lower() == "true"), default=True)
    
    # CNT Page Curl options
    parser.add_argument("--cnt-page-curl-prob", type=float, default=0.0)
    parser.add_argument("--cnt-page-curl-direction", type=str, default="random")
    parser.add_argument("--cnt-page-curl-bending-factor", type=float, default=0.15)
    parser.add_argument("--cnt-page-curl-compression-factor", type=float, default=0.5)
    parser.add_argument("--cnt-page-curl-width-ratio", type=float, default=0.3)
    args = parser.parse_args()

    if not os.path.exists(args.manifest):
        print(f"Manifest not found: {args.manifest}")
        sys.exit(1)

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    labeled_items = [
        item for item in manifest.values()
        if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
    ]

    if not labeled_items:
        print("No Cherokee labeled items found.")
        sys.exit(1)

    def should_skip_binarization(item):
        return item.get("dataset") == "cnt"

    # Replicate exact train/test splitting logic
    train_items = []
    test_items = []
    
    accumulator = 0.0
    for item in labeled_items:
        # Check if pre-assigned split field is present
        if "split" in item:
            if item["split"] == "train":
                train_items.append(item)
            elif item["split"] == "test":
                test_items.append(item)
            else:
                train_items.append(item)
        else:
            accumulator += (1.0 - args.split)
            if accumulator >= 1.0:
                test_items.append(item)
                accumulator -= 1.0
            else:
                train_items.append(item)

    print(f"[Dynamic Augmentation] Total: {len(labeled_items)}. Train (only to be augmented): {len(train_items)}")

    os.makedirs(args.output_dir, exist_ok=True)
    
    # Pre-collect all train image paths for mixup bleed-through
    train_img_paths = []
    for item in train_items:
        path = os.path.join("training_data", item["image_path"])
        if os.path.exists(path):
            train_img_paths.append(path)

    # Load rare characters list
    rare_chars = set()
    rare_chars_path = "training_data/rare_characters.json"
    if os.path.exists(rare_chars_path):
        try:
            with open(rare_chars_path, "r", encoding="utf-8") as f:
                rare_chars = set(json.load(f))
            print(f"[Dynamic Augmentation] Loaded {len(rare_chars)} rare characters from {rare_chars_path}.")
        except Exception as e:
            print(f"Warning: Failed to load rare characters: {e}")

    metadata_records = []

    print(f"Processing and compiling {len(train_items)} train items in a pipelined architecture...")
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
    
    num_cores = os.cpu_count() or 4
    
    with ProcessPoolExecutor(max_workers=num_cores) as gen_executor, \
         ThreadPoolExecutor(max_workers=num_cores * 2) as compile_executor:
         
        compilation_futures = []
        generation_futures = {
            gen_executor.submit(generate_variations_worker, item, train_img_paths, args, rare_chars): item
            for item in train_items
        }
        
        for idx, fut in enumerate(as_completed(generation_futures)):
            try:
                records = fut.result()
                if records:
                    metadata_records.extend(records)
                    if args.compile_lstmf:
                        for r in records:
                            comp_fut = compile_executor.submit(compile_image, r["tiff_path"], args.model_dir)
                            compilation_futures.append((r, comp_fut))
            except Exception as e:
                print(f"Error generating variation: {e}", file=sys.stderr)
                
            if (idx + 1) % 50 == 0 or (idx + 1) == len(train_items):
                print(f"Generation Progress: {idx + 1}/{len(train_items)} items processed.")
                
        if compilation_futures:
            print(f"Waiting for {len(compilation_futures)} compilation tasks to finish...")
            for idx, (record, comp_fut) in enumerate(compilation_futures):
                try:
                    lstmf_path = comp_fut.result()
                    record["lstmf_path"] = lstmf_path
                except Exception as e:
                    print(f"Error compiling {record['tiff_path']}: {e}", file=sys.stderr)
                
                if (idx + 1) % 100 == 0 or (idx + 1) == len(compilation_futures):
                    print(f"Compilation Progress: {idx + 1}/{len(compilation_futures)} compiled.")

    print(f"Dynamic augmentation complete. Generated variations in {args.output_dir}")

    # Write metadata index
    metadata_index_path = args.metadata_index
    if not metadata_index_path:
        metadata_index_path = os.path.join(args.output_dir, "metadata_index.json")
        
    with open(metadata_index_path, "w", encoding="utf-8") as f:
        json.dump(metadata_records, f, indent=2, ensure_ascii=False)
    print(f"Wrote metadata index containing {len(metadata_records)} records to {metadata_index_path}")

if __name__ == "__main__":
    main()

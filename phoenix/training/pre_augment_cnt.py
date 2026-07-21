#!/usr/bin/env python3
"""
Pre-augment and cache the Cherokee New Testament (CNT) dataset.
Applies target heavy noise/augmentation parameters upfront, saves binarized 1-bit TIFFs,
box files, ground truths, and optionally compiles them to .lstmf files to accelerate sweeps.
"""
import os
import sys
import json
import random
import cv2
import argparse
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phoenix.config import TrainingConfig
from phoenix.training.augment import (
    normalize_height,
    generate_box_file,
    get_albumentations_pipeline,
    apply_ink_wash_smudge
)
from phoenix.text.normalization import normalize_truth

def compile_image(img_path, model_dir):
    """
    Compiles a single PNG/TIFF image to .lstmf using tesseract.
    """
    import subprocess
    import glob
    base = os.path.splitext(img_path)[0]
    lstm_train_config = "/opt/homebrew/share/tessdata/configs/lstm.train"
    if not os.path.exists(lstm_train_config):
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

def augment_worker(item_info, output_dir, variations, config_noise, compile_lstmf, model_dir):
    """
    Worker task to augment a single CNT line.
    """
    cv2.setNumThreads(0)
    cnt_pipeline = get_albumentations_pipeline(
        blur_prob=config_noise["blur"]["prob"],
        shadow_prob=config_noise["shadow"]["prob"],
        distortion_prob=config_noise["distortion"]["prob"],
        dropout_prob=config_noise["dropout"]["prob"],
        blur_limit=(config_noise["blur"]["limit_min"], config_noise["blur"]["limit_max"]),
        shadow_dimension=config_noise["shadow"]["dimension"],
        distortion_limit=config_noise["distortion"]["limit"],
        dropout_holes_range=(config_noise["dropout"]["holes_min"], config_noise["dropout"]["holes_max"]),
        dropout_size_range=(config_noise["dropout"]["size_min"], config_noise["dropout"]["size_max"]),
        micro_dropout_prob=config_noise["micro_dropout"]["prob"],
        micro_dropout_holes_range=(config_noise["micro_dropout"]["holes_min"], config_noise["micro_dropout"]["holes_max"]),
        micro_dropout_size_range=(config_noise["micro_dropout"]["size_min"], config_noise["micro_dropout"]["size_max"]),
        elastic_alpha=config_noise["distortion"].get("elastic_alpha", 1.0),
        elastic_sigma=config_noise["distortion"].get("elastic_sigma", 15.0),
        use_multi_scale=config_noise["distortion"].get("use_multi_scale", True),
        page_curl_prob=config_noise.get("page_curl", {}).get("prob", 0.0),
        page_curl_direction=config_noise.get("page_curl", {}).get("direction", "random"),
        page_curl_bending_factor=config_noise.get("page_curl", {}).get("bending_factor", 0.15),
        page_curl_compression_factor=config_noise.get("page_curl", {}).get("compression_factor", 0.5),
        page_curl_width_ratio=config_noise.get("page_curl", {}).get("width_ratio", 0.3)
    )

    image_path = os.path.join("training_data", item_info["image_path"])
    img = cv2.imread(image_path)
    if img is None:
        return []

    label = normalize_truth(item_info["label"])
    item_id = item_info["id"]

    records = []
    for var_idx in range(variations):
        try:
            augmented = cnt_pipeline(image=img)["image"]
            smudge_prob = config_noise.get("smudge", {}).get("prob", 0.4)
            smudge_intensity = config_noise.get("smudge", {}).get("intensity", 0.3)
            if random.random() < smudge_prob:
                augmented = apply_ink_wash_smudge(augmented, intensity=smudge_intensity)

            gray = cv2.cvtColor(augmented, cv2.COLOR_BGR2GRAY) if len(augmented.shape) == 3 else augmented
            norm_img = normalize_height(gray, pad_y=3)
            h, w = norm_img.shape[:2]

            out_name = f"{item_id}_cached_{var_idx}"
            out_base = os.path.join(output_dir, out_name)

            pil_img = Image.fromarray(norm_img).convert('1')
            pil_img.save(out_base + ".tiff", compression="group4")

            gt_path = out_base + ".gt.txt"
            with open(gt_path, "w", encoding="utf-8") as f:
                f.write(label + "\n")

            box_path = out_base + ".box"
            generate_box_file(box_path, label, w, h)

            lstmf_path = None
            if compile_lstmf:
                try:
                    lstmf_path = compile_image(out_base + ".tiff", model_dir)
                except Exception as e:
                    print(f"Warning: Failed to compile {out_base}.tiff: {e}")

            records.append({
                "id": item_id,
                "dataset": "cnt",
                "variation_id": out_name,
                "tiff_path": os.path.abspath(out_base + ".tiff"),
                "gt_path": os.path.abspath(gt_path),
                "box_path": os.path.abspath(box_path),
                "lstmf_path": lstmf_path,
                "label": label,
                "variation": var_idx
            })
        except Exception as ex:
            print(f"Error processing variation {var_idx} for item {item_id}: {ex}")

    return records

def main():
    parser = argparse.ArgumentParser(description="Pre-augment and cache CNT samples.")
    parser.add_argument("--config", default=None, help="Path to TrainingConfig JSON to fetch cnt_noise config")
    parser.add_argument("--output-dir", default="training_data/cnt_cache", help="Output cache directory")
    parser.add_argument("--cnt-dir", default="training_data/cnt", help="Directory where book_XX aligned manifests live")
    parser.add_argument("--variations-per-image", type=int, default=3, help="Variations per CNT image")
    parser.add_argument("--compile-lstmf", action="store_true", help="Compile augmented images to .lstmf")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Directory with base chr.traineddata")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of source CNT lines to pre-augment")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 1. Fetch config or use defaults
    cfg = TrainingConfig()
    if args.config and os.path.exists(args.config):
        cfg = TrainingConfig.load_from_json(args.config)

    # 2. Find all valid CNT lines
    all_valid_cnt_lines = []
    for book_idx in range(1, 28):
        book_dir = os.path.join(args.cnt_dir, f"book_{book_idx:02d}")
        cnt_manifest_path = os.path.join(book_dir, "aligned_manifest.json")
        if not os.path.exists(cnt_manifest_path):
            continue
        
        with open(cnt_manifest_path, "r", encoding="utf-8") as f:
            aligned_manifest = json.load(f)
        
        for verse_key in sorted(aligned_manifest.keys()):
            verse = aligned_manifest[verse_key]
            for line_idx, line in enumerate(verse.get("lines", [])):
                ftm_aligned = line.get("ftm_aligned", "").strip()
                if ftm_aligned:
                    item_id = f"cnt_{book_idx:02d}_{verse_key}_line_{line_idx:02d}"
                    image_path = f"cnt/book_{book_idx:02d}/line_crops/{verse_key}_line_{line_idx:02d}.png"
                    all_valid_cnt_lines.append({
                        "id": item_id,
                        "image_path": image_path,
                        "label": ftm_aligned
                    })

    if args.limit:
        random.seed(42)
        all_valid_cnt_lines = random.sample(all_valid_cnt_lines, min(args.limit, len(all_valid_cnt_lines)))

    print(f"Found {len(all_valid_cnt_lines)} valid CNT lines. Starting pre-augmentation...")

    # 3. Augment in parallel
    cache_manifest = {}
    import multiprocessing
    num_cores = max(1, multiprocessing.cpu_count() - 1)

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = {
            executor.submit(
                augment_worker,
                item,
                args.output_dir,
                args.variations_per_image,
                cfg.cnt_noise,
                args.compile_lstmf,
                args.model_dir
            ): item["id"]
            for item in all_valid_cnt_lines
        }

        completed = 0
        for future in as_completed(futures):
            item_id = futures[future]
            completed += 1
            if completed % 100 == 0 or completed == len(all_valid_cnt_lines):
                print(f"Progress: {completed}/{len(all_valid_cnt_lines)} lines augmented")

            try:
                records = future.result()
                if records:
                    cache_manifest[item_id] = records
            except Exception as e:
                print(f"Error for item {item_id}: {e}")

    # 4. Save cache manifest
    manifest_path = os.path.join(args.output_dir, "cnt_cache_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(cache_manifest, f, ensure_ascii=False, indent=2)

    print(f"Pre-augmentation complete. Saved cache manifest with {len(cache_manifest)} items to {manifest_path}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
evaluate_mixed_model.py

Evaluates a given .traineddata model against the Phoenix test split (test/base)
and the Cherokee New Testament (CNT) test split (test/cnt) using Tesseract.
Computes Character Error Rate (CER) and Word Error Rate (WER) for both splits
separately and computes a weighted overall average.
"""

import os
import re
import sys
import glob
import argparse
import subprocess
import unicodedata

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from phoenix.text.normalization import normalize_truth

def norm(s: str) -> str:
    return normalize_truth(s)

def edit_distance(a, b) -> int:
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for item_a in a:
        curr = [prev[0] + 1] + [0] * lb
        for j, item_b in enumerate(b, 1):
            curr[j] = prev[j - 1] if item_a == item_b else 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[lb]

def compute_cer(truth: str, ocr: str) -> float:
    truth_norm = norm(truth).strip()
    ocr_norm = norm(ocr).strip()
    if not truth_norm:
        return 100.0 if ocr_norm else 0.0
    return min(100.0, 100.0 * edit_distance(truth_norm, ocr_norm) / len(truth_norm))

def compute_wer(truth: str, ocr: str) -> float:
    t_words = norm(truth).strip().split()
    o_words = norm(ocr).strip().split()
    if not t_words:
        return 100.0 if o_words else 0.0
    return min(100.0, 100.0 * edit_distance(t_words, o_words) / len(t_words))

def recognize_line(img_path: str, tessdata_dir: str, lang: str) -> str:
    cmd = [
        "tesseract",
        img_path,
        "stdout",
        "--tessdata-dir", tessdata_dir,
        "-l", lang,
        "--oem", "1",
        "--psm", "13"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip()

def evaluate_directory(dir_path: str, tessdata_dir: str, lang: str):
    png_files = sorted(glob.glob(os.path.join(dir_path, "*.png")))
    if not png_files:
        print(f"No PNG files found in {dir_path}")
        return None

    results = []
    total_cer = 0.0
    total_wer = 0.0

    print(f"Evaluating {len(png_files)} files in {dir_path}...")
    for idx, png_file in enumerate(png_files):
        gt_file = os.path.splitext(png_file)[0] + ".gt.txt"
        if not os.path.exists(gt_file):
            continue
        with open(gt_file, "r", encoding="utf-8") as f:
            truth = f.read().strip()
        
        ocr = recognize_line(png_file, tessdata_dir, lang)
        line_cer = compute_cer(truth, ocr)
        line_wer = compute_wer(truth, ocr)
        results.append({
            "file": os.path.basename(png_file),
            "truth": truth,
            "ocr": ocr,
            "cer": line_cer,
            "wer": line_wer
        })
        total_cer += line_cer
        total_wer += line_wer

    mean_cer = total_cer / len(results) if results else 0.0
    mean_wer = total_wer / len(results) if results else 0.0

    return {
        "count": len(results),
        "mean_cer": mean_cer,
        "mean_wer": mean_wer,
        "results": results
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate mixed OCR dataset performance.")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Tessdata directory containing the model")
    parser.add_argument("--lang", default="chr", help="Language model prefix to use (default: chr)")
    parser.add_argument("--dataset-dir", default="training_data/dataset", help="Dataset root directory")
    args = parser.parse_args()

    # Determine paths
    phoenix_test_dir = os.path.join(args.dataset_dir, "test", "base")
    cnt_test_dir = os.path.join(args.dataset_dir, "test", "cnt")

    print(f"=== Starting Mixed Model Evaluation ===")
    print(f"Tessdata directory: {args.model_dir}")
    print(f"Language model: {args.lang}")

    phoenix_stats = evaluate_directory(phoenix_test_dir, args.model_dir, args.lang)
    cnt_stats = evaluate_directory(cnt_test_dir, args.model_dir, args.lang)

    print("\n================ EVALUATION SUMMARY ================")
    
    total_count = 0
    weighted_cer_sum = 0.0
    weighted_wer_sum = 0.0

    if phoenix_stats:
        print(f"Phoenix Test Set ({phoenix_stats['count']} lines):")
        print(f"  Mean CER: {phoenix_stats['mean_cer']:.2f}%")
        print(f"  Mean WER: {phoenix_stats['mean_wer']:.2f}%")
        total_count += phoenix_stats['count']
        weighted_cer_sum += phoenix_stats['mean_cer'] * phoenix_stats['count']
        weighted_wer_sum += phoenix_stats['mean_wer'] * phoenix_stats['count']
    else:
        print("Phoenix Test Set: Not found or empty.")

    if cnt_stats:
        print(f"CNT Test Set ({cnt_stats['count']} lines):")
        print(f"  Mean CER: {cnt_stats['mean_cer']:.2f}%")
        print(f"  Mean WER: {cnt_stats['mean_wer']:.2f}%")
        total_count += cnt_stats['count']
        weighted_cer_sum += cnt_stats['mean_cer'] * cnt_stats['count']
        weighted_wer_sum += cnt_stats['mean_wer'] * cnt_stats['count']
    else:
        print("CNT Test Set: Not found or empty.")

    if total_count > 0:
        overall_cer = weighted_cer_sum / total_count
        overall_wer = weighted_wer_sum / total_count
        print(f"\nOverall Combined Weighted Performance ({total_count} lines total):")
        print(f"  Weighted Mean CER: {overall_cer:.2f}%")
        print(f"  Weighted Mean WER: {overall_wer:.2f}%")
    else:
        print("\nNo items evaluated.")

if __name__ == "__main__":
    main()

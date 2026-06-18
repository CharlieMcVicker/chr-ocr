#!/usr/bin/env python3
import os
import sys
import glob
import random
import difflib
import numpy as np
import cv2
import doxapy
import subprocess
from Levenshtein import distance as edit_distance
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from phoenix.text.normalization import normalize_truth

def norm(s: str) -> str:
    return normalize_truth(s)

def compute_cer(truth: str, ocr: str) -> float:
    truth_norm = norm(truth).strip()
    ocr_norm = norm(ocr).strip()
    if not truth_norm:
        return 100.0 if ocr_norm else 0.0
    return min(100.0, 100.0 * edit_distance(truth_norm, ocr_norm) / len(truth_norm))

def align3_dp(s1, s2, s3):
    L1, L2, L3 = len(s1), len(s2), len(s3)
    dp = np.zeros((L1+1, L2+1, L3+1), dtype=int)
    for i in range(L1+1):
        for j in range(L2+1):
            for k in range(L3+1):
                if i == 0 and j == 0 and k == 0:
                    continue
                opts = []
                if i > 0: opts.append(dp[i-1, j, k] + 1)
                if j > 0: opts.append(dp[i, j-1, k] + 1)
                if k > 0: opts.append(dp[i, j, k-1] + 1)
                if i > 0 and j > 0: opts.append(dp[i-1, j-1, k] + (0 if s1[i-1]==s2[j-1] else 1))
                if i > 0 and k > 0: opts.append(dp[i-1, j, k-1] + (0 if s1[i-1]==s3[k-1] else 1))
                if j > 0 and k > 0: opts.append(dp[i, j-1, k-1] + (0 if s2[j-1]==s3[k-1] else 1))
                if i > 0 and j > 0 and k > 0:
                    c1, c2, c3 = s1[i-1], s2[j-1], s3[k-1]
                    if c1 == c2 == c3: cost = 0
                    elif c1 == c2 or c1 == c3 or c2 == c3: cost = 1
                    else: cost = 2
                    opts.append(dp[i-1, j-1, k-1] + cost)
                dp[i, j, k] = min(opts)
    
    i, j, k = L1, L2, L3
    res1, res2, res3 = [], [], []
    while i > 0 or j > 0 or k > 0:
        c1 = s1[i-1] if i > 0 else ''
        c2 = s2[j-1] if j > 0 else ''
        c3 = s3[k-1] if k > 0 else ''
        current = dp[i, j, k]
        
        if i>0 and j>0 and k>0:
            cost = 0 if c1==c2==c3 else (1 if (c1==c2 or c1==c3 or c2==c3) else 2)
            if current == dp[i-1, j-1, k-1] + cost:
                res1.append(c1); res2.append(c2); res3.append(c3)
                i-=1; j-=1; k-=1; continue
        if i>0 and j>0:
            cost = 0 if c1==c2 else 1
            if current == dp[i-1, j-1, k] + cost:
                res1.append(c1); res2.append(c2); res3.append('')
                i-=1; j-=1; continue
        if i>0 and k>0:
            cost = 0 if c1==c3 else 1
            if current == dp[i-1, j, k-1] + cost:
                res1.append(c1); res2.append(''); res3.append(c3)
                i-=1; k-=1; continue
        if j>0 and k>0:
            cost = 0 if c2==c3 else 1
            if current == dp[i, j-1, k-1] + cost:
                res1.append(''); res2.append(c2); res3.append(c3)
                j-=1; k-=1; continue
        if i>0 and current == dp[i-1, j, k] + 1:
            res1.append(c1); res2.append(''); res3.append('')
            i-=1; continue
        if j>0 and current == dp[i, j-1, k] + 1:
            res1.append(''); res2.append(c2); res3.append('')
            j-=1; continue
        if k>0 and current == dp[i, j, k-1] + 1:
            res1.append(''); res2.append(''); res3.append(c3)
            k-=1; continue

    res1.reverse(); res2.reverse(); res3.reverse()
    final = []
    for x, y, z in zip(res1, res2, res3):
        counts = {}
        for char in (x, y, z):
            if char: counts[char] = counts.get(char, 0) + 1
        if counts:
            best_char = max(counts, key=counts.get)
            final.append(best_char)
            
    return "".join(final)

def binarize(img, algo_name):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if algo_name == "grayscale":
        return img
    elif algo_name == "sauvola":
        algo = doxapy.Binarization.Algorithms.SAUVOLA
        return doxapy.to_binary(algo, img, {"window": 45, "k": 0.1})
    elif algo_name == "wolf":
        algo = doxapy.Binarization.Algorithms.WOLF
        return doxapy.to_binary(algo, img, {"window": 45, "k": 0.1})
    return img

def recognize_line(img_path: str, tessdata_dir: str, lang: str) -> str:
    cmd = [
        "tesseract", img_path, "stdout",
        "--tessdata-dir", tessdata_dir,
        "-l", lang, "--oem", "1", "--psm", "13"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip()

def main():
    test_dir = "training_data/dataset/test/base"
    png_files = sorted(glob.glob(os.path.join(test_dir, "*.png")))
    random.seed(42)
    random.shuffle(png_files)
    subset = []
    for f in png_files:
        gt_file = f.replace(".png", ".gt.txt")
        if os.path.exists(gt_file):
            subset.append((f, gt_file))
            
    tessdata_dir = "training_data/dataset/model"
    lang = "chr_best_finetuned"
    
    total_base_cer = 0.0
    total_ensemble_cer = 0.0
    
    temp_dir = "tmp_ensemble"
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Evaluating {len(subset)} crops...")
    for idx, (img_path, gt_path) in enumerate(tqdm(subset)):
        with open(gt_path, "r", encoding="utf-8") as f:
            truth = f.read().strip()
            
        img = cv2.imread(img_path)
        
        # Base Grayscale
        base_img = binarize(img, "grayscale")
        base_path = os.path.join(temp_dir, f"base_{idx}.png")
        cv2.imwrite(base_path, base_img)
        base_ocr = recognize_line(base_path, tessdata_dir, lang)
        
        # Sauvola
        sauvola_img = binarize(img, "sauvola")
        sauvola_path = os.path.join(temp_dir, f"sauvola_{idx}.png")
        cv2.imwrite(sauvola_path, sauvola_img)
        sauvola_ocr = recognize_line(sauvola_path, tessdata_dir, lang)
        
        # Wolf
        wolf_img = binarize(img, "wolf")
        wolf_path = os.path.join(temp_dir, f"wolf_{idx}.png")
        cv2.imwrite(wolf_path, wolf_img)
        wolf_ocr = recognize_line(wolf_path, tessdata_dir, lang)
        
        # Voting
        ensemble_ocr = align3_dp(base_ocr, sauvola_ocr, wolf_ocr)
        
        base_cer = compute_cer(truth, base_ocr)
        ensemble_cer = compute_cer(truth, ensemble_ocr)
        
        total_base_cer += base_cer
        total_ensemble_cer += ensemble_cer
        
    print(f"Base Grayscale CER: {total_base_cer / len(subset):.3f}%")
    print(f"Ensemble Voting CER: {total_ensemble_cer / len(subset):.3f}%")

if __name__ == "__main__":
    main()

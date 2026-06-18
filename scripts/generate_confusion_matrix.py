#!/usr/bin/env python3
"""
generate_confusion_matrix.py

Loads ground truth and OCR predictions on the test set, performs character-level alignment
to identify insertions, deletions, and substitutions, and generates a formatted
confusion matrix (CSV and Markdown) of the top confused character pairs.
"""

import os
import sys
import glob
import csv
import argparse
import subprocess
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from phoenix.text.normalization import normalize_truth

def norm(s: str) -> str:
    return normalize_truth(s)

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

def align(truth: str, ocr: str):
    """
    Perform DP alignment between normalized truth and OCR predicted strings.
    Returns a list of tuples: (truth_char, predicted_char, type)
    where type is 'match', 'substitution', 'deletion', or 'insertion'.
    """
    la, lb = len(truth), len(ocr)
    dp = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        dp[i][0] = i
    for j in range(lb + 1):
        dp[0][j] = j
    
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            if truth[i-1] == ocr[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j-1],  # substitution
                    dp[i-1][j],    # deletion
                    dp[i][j-1]     # insertion
                )
    
    # Backtrack to reconstruct alignment
    i, j = la, lb
    alignment = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and truth[i-1] == ocr[j-1]:
            alignment.append((truth[i-1], ocr[j-1], "match"))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            alignment.append((truth[i-1], ocr[j-1], "substitution"))
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i-1][j] + 1):
            alignment.append((truth[i-1], "", "deletion"))
            i -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j-1] + 1):
            alignment.append(("", ocr[j-1], "insertion"))
            j -= 1
        else:
            # Fallback
            if i > 0 and j > 0:
                alignment.append((truth[i-1], ocr[j-1], "substitution"))
                i -= 1
                j -= 1
            elif i > 0:
                alignment.append((truth[i-1], "", "deletion"))
                i -= 1
            else:
                alignment.append(("", ocr[j-1], "insertion"))
                j -= 1
                
    alignment.reverse()
    return alignment

def evaluate_directory(dir_path: str, tessdata_dir: str, lang: str):
    png_files = sorted(glob.glob(os.path.join(dir_path, "*.png")))
    if not png_files:
        print(f"No PNG files found in {dir_path}")
        return []

    print(f"Processing {len(png_files)} files in {dir_path}...")
    alignments = []
    for png_file in png_files:
        gt_file = os.path.splitext(png_file)[0] + ".gt.txt"
        if not os.path.exists(gt_file):
            continue
        with open(gt_file, "r", encoding="utf-8") as f:
            truth = f.read().strip()
        
        ocr = recognize_line(png_file, tessdata_dir, lang)
        
        truth_norm = norm(truth).strip()
        ocr_norm = norm(ocr).strip()
        
        line_alignment = align(truth_norm, ocr_norm)
        alignments.extend(line_alignment)
        
    return alignments

def main():
    parser = argparse.ArgumentParser(description="Generate character-level OCR confusion matrix.")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Tessdata directory containing the model")
    parser.add_argument("--lang", default="chr", help="Language model prefix to use (default: chr)")
    parser.add_argument("--dataset-dir", default="training_data/dataset", help="Dataset root directory")
    parser.add_argument("--output-dir", default="training_data/performance_analysis", help="Output directory for reports")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    phoenix_test_dir = os.path.join(args.dataset_dir, "test", "base")
    cnt_test_dir = os.path.join(args.dataset_dir, "test", "cnt")

    print(f"=== Character Confusion Matrix Analysis ===")
    print(f"Tessdata directory: {args.model_dir}")
    print(f"Language model: {args.lang}")

    alignments = []
    if os.path.exists(phoenix_test_dir):
        alignments.extend(evaluate_directory(phoenix_test_dir, args.model_dir, args.lang))
    if os.path.exists(cnt_test_dir):
        alignments.extend(evaluate_directory(cnt_test_dir, args.model_dir, args.lang))

    if not alignments:
        print("No characters aligned. Check model or dataset path.")
        sys.exit(1)

    # Accumulate confusion statistics
    all_truth_chars = set()
    all_pred_chars = set()
    
    sub_counts = defaultdict(lambda: defaultdict(int))
    del_counts = defaultdict(int)
    ins_counts = defaultdict(int)
    match_counts = defaultdict(int)
    truth_char_total = defaultdict(int)

    for truth_char, pred_char, err_type in alignments:
        if truth_char:
            all_truth_chars.add(truth_char)
            truth_char_total[truth_char] += 1
        if pred_char:
            all_pred_chars.add(pred_char)

        if err_type == "match":
            match_counts[truth_char] += 1
            sub_counts[truth_char][truth_char] += 1
        elif err_type == "substitution":
            sub_counts[truth_char][pred_char] += 1
        elif err_type == "deletion":
            del_counts[truth_char] += 1
        elif err_type == "insertion":
            ins_counts[pred_char] += 1

    # 1. Output CSV Confusion Matrix
    # We want a CSV where rows are truth characters and columns are predicted characters (including deletions/insertions)
    all_chars = sorted(list(all_truth_chars | all_pred_chars))
    csv_path = os.path.join(args.output_dir, "confusion_matrix.csv")
    
    with open(csv_path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Header row: Truth / Predicted, followed by all predicted characters, and then Deletions
        writer.writerow(["Truth \\ Predicted"] + all_chars + ["<del>"])
        
        for tc in all_chars:
            row = [tc]
            for pc in all_chars:
                count = sub_counts[tc][pc] if tc in all_truth_chars else (ins_counts[pc] if tc == "" else 0)
                row.append(count)
            # Add deletion count
            row.append(del_counts[tc] if tc in all_truth_chars else 0)
            writer.writerow(row)

    print(f"Full confusion matrix written to {csv_path}")

    # 2. Extract top confused pairs (substitutions where truth != predicted)
    confused_pairs = []
    for tc in all_truth_chars:
        for pc in sub_counts[tc]:
            if tc != pc and sub_counts[tc][pc] > 0:
                confused_pairs.append((tc, pc, sub_counts[tc][pc]))
    confused_pairs.sort(key=lambda x: x[2], reverse=True)

    top_deletions = sorted(del_counts.items(), key=lambda x: x[1], reverse=True)
    top_insertions = sorted(ins_counts.items(), key=lambda x: x[1], reverse=True)

    # 3. Create Markdown Report
    md_path = os.path.join(args.output_dir, "confusion_matrix.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Character-Level OCR Confusion Matrix Report\n\n")
        f.write("This report provides analysis of character-level substitution, deletion, and insertion errors to identify which Cherokee syllables/characters the fine-tuned model frequently confuses.\n\n")
        
        # Summary statistics
        total_truth = sum(truth_char_total.values())
        total_matches = sum(match_counts.values())
        total_subs = sum(count for _, _, count in confused_pairs)
        total_dels = sum(del_counts.values())
        total_ins = sum(ins_counts.values())
        
        f.write("## Overall Statistics\n")
        f.write(f"- **Total Characters in Ground Truth**: {total_truth}\n")
        f.write(f"- **Total Matches (Correct)**: {total_matches} ({total_matches/total_truth*100:.2f}% accuracy)\n")
        f.write(f"- **Total Substitutions**: {total_subs} ({total_subs/total_truth*100:.2f}% substitution rate)\n")
        f.write(f"- **Total Deletions**: {total_dels} ({total_dels/total_truth*100:.2f}% deletion rate)\n")
        f.write(f"- **Total Insertions**: {total_ins} ({total_ins/total_truth*100:.2f}% insertion rate)\n\n")

        f.write("## Top 30 Confused Character Pairs (Substitutions)\n")
        f.write("| Truth | Predicted | Count | Context / Potential Reason |\n")
        f.write("| :---: | :-------: | :---: | :------------------------- |\n")
        for tc, pc, count in confused_pairs[:30]:
            f.write(f"| `{tc}` | `{pc}` | {count} | |\n")
        f.write("\n")

        f.write("## Top 15 Deleted Characters\n")
        f.write("| Character | Deletion Count | Total in GT | Deletion Rate |\n")
        f.write("| :-------: | :------------: | :---------: | :------------: |\n")
        for char, count in top_deletions[:15]:
            total = truth_char_total[char]
            rate = (count / total * 100) if total > 0 else 0.0
            f.write(f"| `{char}` | {count} | {total} | {rate:.2f}% |\n")
        f.write("\n")

        f.write("## Top 15 Inserted Characters\n")
        f.write("| Character | Insertion Count |\n")
        f.write("| :-------: | :-------------: |\n")
        for char, count in top_insertions[:15]:
            f.write(f"| `{char}` | {count} |\n")
        f.write("\n")

    print(f"Markdown report written to {md_path}")

    # Output top 10 confusions to console for quick visibility
    print("\n--- TOP 10 CONFUSED CHARACTER PAIRS ---")
    for tc, pc, count in confused_pairs[:10]:
        print(f"  Truth '{tc}' -> Predicted '{pc}': {count} times")

if __name__ == "__main__":
    main()

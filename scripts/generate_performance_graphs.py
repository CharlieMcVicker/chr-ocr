#!/usr/bin/env python3
"""
generate_performance_graphs.py

Evaluates a Tesseract OCR checkpoint against a test set and produces:
  1. A histogram of Character Error Rate (CER) across all lines.
  2. A bar chart of mean CER grouped by document page.
  3. A markdown performance report.

Strategy:
  - Read every .gt.txt from disk, keyed to its .lstmf path (ordered).
  - Run lstmeval ONCE on the full list.test (model loads once = fast).
  - lstmeval makes two internal passes over the file list; only the FIRST
    occurrence of each truth/file's output is used (we consume the pairs
    list greedily in file-list order, skipping any pair whose truth we've
    already consumed).
  - Files whose truth never appears in the emitted pairs (encoding errors
    skipped by lstmeval, or missing .gt.txt) are assigned CER = 100%.
"""
import os
import re
import sys
import glob
import argparse
import subprocess
import unicodedata
import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def norm(s: str) -> str:
    """NFC-normalise to handle any Unicode form differences."""
    return unicodedata.normalize("NFC", s)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein character edit distance."""
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for ca in a:
        curr = [prev[0] + 1] + [0] * lb
        for j, cb in enumerate(b, 1):
            curr[j] = prev[j - 1] if ca == cb else 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[lb]


def cer(truth: str, ocr: str) -> float:
    """Character Error Rate as a percentage. Returns 100.0 if truth is empty."""
    if not truth:
        return 100.0
    return min(100.0, 100.0 * edit_distance(truth, ocr) / len(truth))


def parse_filename_metadata(filepath: str) -> tuple[str, str, str]:
    """
    Extracts doc_id and line_id from a filepath.
    Pattern:  YYYY-MM-DD_seq-N_col_CC_line_LLL[_augment].lstmf
    Or:       cnt_BB_VVVVVV_line_LL
    """
    filename = os.path.basename(filepath)
    base_name = os.path.splitext(filename)[0]
    
    # Check if CNT pattern
    if base_name.startswith("cnt_"):
        parts = base_name.split("_")
        doc_id = "_".join(parts[:3]) # e.g. cnt_01_010101
        line_id = "_".join(parts[3:5]) # e.g. line_00
        return doc_id, line_id, base_name
        
    doc_match = re.match(r"^(\d{4}-\d{2}-\d{2}_seq-\d+)", base_name)
    doc_id = doc_match.group(1) if doc_match else "unknown_doc"
    line_match = re.search(r"(line_\d+)", base_name)
    line_id = line_match.group(1) if line_match else "unknown_line"
    return doc_id, line_id, base_name


# ---------------------------------------------------------------------------
# Ground-truth loading
# ---------------------------------------------------------------------------

def load_ground_truths(lstmf_files: list[str]) -> list[dict]:
    """
    For every lstmf path, load its .gt.txt companion from disk.
    Returns an ordered list of dicts (one per lstmf file).
    """
    entries = []
    for lstmf_path in lstmf_files:
        base = os.path.splitext(lstmf_path)[0]
        gt_path = base + ".gt.txt"
        doc_id, line_id, base_name = parse_filename_metadata(lstmf_path)
        if os.path.exists(gt_path):
            try:
                truth = open(gt_path, encoding="utf-8").read().strip()
            except Exception:
                truth = ""
        else:
            truth = ""
        entries.append({
            "lstmf_path": lstmf_path,
            "truth": truth,
            "norm_truth": norm(truth),
            "base_name": base_name,
            "doc_id": doc_id,
            "line_id": line_id,
        })
    return entries


# ---------------------------------------------------------------------------
# lstmeval runner & parser
# ---------------------------------------------------------------------------

def run_lstmeval(checkpoint_path: str, traineddata_path: str, list_file: str) -> str:
    """Run lstmeval once; return stderr (Truth/OCR pairs appear there)."""
    cmd = [
        "lstmeval",
        "--model", checkpoint_path,
        "--traineddata", traineddata_path,
        "--eval_listfile", list_file,
    ]
    print("Running: " + " ".join(cmd))
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stderr


def parse_truth_ocr_pairs(lstmeval_output: str) -> list[tuple[str, str]]:
    """
    Extract ALL (truth, ocr) pairs from lstmeval stderr in order.
    Note: lstmeval does two internal passes so each file is emitted twice
    (with different OCR outputs per pass). We keep all of them; the
    assignment logic below picks only the first matching occurrence per file.
    """
    pairs: list[tuple[str, str]] = []
    lines = lstmeval_output.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("Truth:"):
            truth = lines[i][len("Truth:"):].strip()
            j = i + 1
            while j < len(lines) and not lines[j].startswith("OCR  :"):
                j += 1
            ocr = lines[j][len("OCR  :"):].strip() if j < len(lines) else ""
            pairs.append((truth, ocr))
            i = j + 1
        else:
            i += 1
    return pairs


# ---------------------------------------------------------------------------
# Assignment: match pairs to files
# ---------------------------------------------------------------------------

def assign_pairs_to_files(
    pairs: list[tuple[str, str]],
    file_entries: list[dict],
) -> list[dict]:
    """
    For each file (in list order), find its FIRST matching pair in the
    emitted pairs by NFC-normalised truth string.

    lstmeval emits each file's truth twice (two passes), so we track
    which (pair_index, file_index) combinations have already been consumed.
    We use a pointer into the pairs list that advances as we consume matches,
    so the first pass is consumed before the second pass is reached.

    Files with no matching pair (encoding error / missing GT) → CER = 100%.
    """
    # Build a forward index: norm_truth → sorted list of pair indices
    from collections import defaultdict
    truth_to_indices: dict[str, list[int]] = defaultdict(list)
    for idx, (truth, _) in enumerate(pairs):
        truth_to_indices[norm(truth)].append(idx)

    # For each truth, we'll pop indices in order (first pass first)
    truth_ptr: dict[str, int] = {}  # norm_truth → current position in its index list

    results = []
    for entry in file_entries:
        norm_t = entry["norm_truth"]
        truth = entry["truth"]
        matched_ocr = None

        if norm_t and norm_t in truth_to_indices:
            indices = truth_to_indices[norm_t]
            ptr = truth_ptr.get(norm_t, 0)
            if ptr < len(indices):
                # Consume this occurrence
                pair_idx = indices[ptr]
                matched_ocr = pairs[pair_idx][1]
                truth_ptr[norm_t] = ptr + 1

        if matched_ocr is not None:
            line_cer = cer(truth, matched_ocr)
            status = "ok"
        else:
            matched_ocr = ""
            line_cer = 100.0
            status = "encoding_error" if truth else "no_gt"

        results.append({
            "file": entry["lstmf_path"],
            "base_name": entry["base_name"],
            "doc_id": entry["doc_id"],
            "line_id": entry["line_id"],
            "truth": truth,
            "ocr": matched_ocr,
            "cer": line_cer,
            "status": status,
        })

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_histogram(cers: list[float], mean_cer: float, median_cer: float, output_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(cers, bins=25, color="#5B9BD5", edgecolor="black", alpha=0.85)
    ax.axvline(mean_cer, color="#E34234", linestyle="--", linewidth=2,
               label=f"Mean: {mean_cer:.2f}%")
    ax.axvline(median_cer, color="#2CA44C", linestyle="--", linewidth=2,
               label=f"Median: {median_cer:.2f}%")
    ax.set_title("Histogram of Character Error Rate (CER) by Line", fontsize=14, fontweight="bold")
    ax.set_xlabel("Character Error Rate (%)", fontsize=12)
    ax.set_ylabel("Number of Lines", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(fontsize=11)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved histogram       → {output_path}")


def plot_barchart(doc_stats: list[dict], overall_mean: float, output_path: str):
    doc_ids = [d["doc_id"].replace("1828-", "") for d in doc_stats]
    mean_cers = [d["mean_cer"] for d in doc_stats]

    fig, ax = plt.subplots(figsize=(max(10, len(doc_ids) * 0.9), 6))
    bars = ax.bar(doc_ids, mean_cers, color="#E07B54", edgecolor="black", alpha=0.85)
    ax.axhline(overall_mean, color="#E34234", linestyle="--", linewidth=1.5,
               label=f"Overall mean: {overall_mean:.2f}%")
    ax.set_title("Mean CER by Document Page", fontsize=14, fontweight="bold")
    ax.set_xlabel("Document Page (1828- prefix omitted)", fontsize=12)
    ax.set_ylabel("Mean CER (%)", fontsize=12)
    ax.set_xticks(range(len(doc_ids)))
    ax.set_xticklabels(doc_ids, rotation=45, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(fontsize=10)
    for bar, val in zip(bars, mean_cers):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved bar chart       → {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate an OCR checkpoint and generate performance graphs."
    )
    parser.add_argument("--checkpoint",
        default="training_data/dataset_staged_output_full/chr_16.457_1987_2300.checkpoint")
    parser.add_argument("--test-dir", default="training_data/dataset/test/base")
    parser.add_argument("--traineddata",
        default="training_data/dataset/model/chr_best_finetuned.traineddata")
    parser.add_argument("--output-dir", default="training_data/performance_analysis")
    args = parser.parse_args()

    for path, label in [
        (args.checkpoint, "checkpoint"),
        (args.test_dir, "test directory"),
        (args.traineddata, "traineddata"),
    ]:
        if not os.path.exists(path):
            print(f"Error: {label} not found at {path}")
            sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    tessdata_dir = os.path.dirname(os.path.abspath(args.traineddata))

    # 1. Discover png files and compile them to lstmf
    png_files = sorted(glob.glob(os.path.join(args.test_dir, "*.png")))
    if not png_files:
        print(f"Error: No .png files found in {args.test_dir}")
        sys.exit(1)

    from concurrent.futures import ThreadPoolExecutor

    def compile_png(img_path):
        base = os.path.splitext(img_path)[0]
        lstmf_path = base + ".lstmf"
        if os.path.exists(lstmf_path):
            os.remove(lstmf_path)
        
        subprocess.run([
            "tesseract",
            img_path,
            base,
            "--tessdata-dir", tessdata_dir,
            "-l", "chr",
            "--oem", "1",
            "--psm", "13",
            "lstm.train"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return lstmf_path

    print(f"Compiling {len(png_files)} images to .lstmf using {args.traineddata}...")
    with ThreadPoolExecutor() as executor:
        lstmf_files = list(executor.map(compile_png, png_files))

    # 2. Load ground truths from disk
    print("Loading ground truth files from disk...")
    file_entries = load_ground_truths(lstmf_files)
    missing_gt = sum(1 for e in file_entries if not e["truth"])
    print(f"  {len(file_entries) - missing_gt} with GT text, {missing_gt} missing.")

    # 3. Write list.test and run lstmeval once
    list_file = os.path.join(args.test_dir, "list.test")
    with open(list_file, "w", encoding="utf-8") as f:
        for p in lstmf_files:
            f.write(os.path.abspath(p) + "\n")

    lstmeval_output = run_lstmeval(args.checkpoint, args.traineddata, list_file)

    # 4. Parse ALL Truth/OCR pairs (includes both internal passes)
    all_pairs = parse_truth_ocr_pairs(lstmeval_output)
    unique_truths_emitted = len({norm(t) for t, _ in all_pairs})
    print(f"Parsed {len(all_pairs)} Truth/OCR pairs ({unique_truths_emitted} unique truths).")

    encoding_error_count = len(lstmf_files) - unique_truths_emitted - missing_gt
    if encoding_error_count > 0:
        print(f"  ~{encoding_error_count} files likely skipped by lstmeval due to encoding errors.")

    # 5. Assign pairs to files (first-occurrence per file)
    results = assign_pairs_to_files(all_pairs, file_entries)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    err_count = len(results) - ok_count
    print(f"Assigned: {ok_count} ok, {err_count} encoding errors / missing GT (CER=100%).")

    # 6. Aggregate stats
    all_cers = [r["cer"] for r in results]
    mean_cer = np.mean(all_cers)
    median_cer = np.median(all_cers)
    clean_cers = [r["cer"] for r in results if r["status"] == "ok"]
    mean_cer_clean = np.mean(clean_cers) if clean_cers else float("nan")

    agg_match = re.search(r"BCER eval=([\d\.]+),\s*BWER eval=([\d\.]+)", lstmeval_output)
    agg_bcer = float(agg_match.group(1)) if agg_match else None
    agg_bwer = float(agg_match.group(2)) if agg_match else None

    print(f"\nResults ({len(results)} lines):")
    print(f"  Mean CER (all)     : {mean_cer:.3f}%")
    print(f"  Mean CER (ok only) : {mean_cer_clean:.3f}%")
    print(f"  Median CER (all)   : {median_cer:.3f}%")
    if agg_bcer is not None:
        print(f"  lstmeval BCER      : {agg_bcer:.3f}%")
        print(f"  lstmeval BWER      : {agg_bwer:.3f}%")

    # 7. Document-level grouping
    doc_groups: dict[str, list[float]] = {}
    for r in results:
        doc_groups.setdefault(r["doc_id"], []).append(r["cer"])
    doc_stats = sorted(
        [{"doc_id": d, "mean_cer": np.mean(c), "median_cer": np.median(c), "count": len(c)}
         for d, c in doc_groups.items()],
        key=lambda x: x["mean_cer"], reverse=True,
    )

    # 8. Plots
    plot_histogram(all_cers, mean_cer, median_cer,
                   os.path.join(args.output_dir, "histogram_loss_by_line.png"))
    plot_barchart(doc_stats, mean_cer,
                  os.path.join(args.output_dir, "barchart_loss_by_document.png"))

    # 9. Markdown report
    report_path = os.path.join(args.output_dir, "performance_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# OCR Model Performance Analysis Report\n\n")
        f.write(f"- **Checkpoint**: `{args.checkpoint}`\n")
        f.write(f"- **Dataset**: `{args.test_dir}` ({len(results)} lines)\n")
        f.write(f"- **Encoding errors / missing GT**: {err_count} lines (CER forced to 100%)\n\n")
        f.write("## Overall Metrics\n\n")
        f.write("| Metric | Value |\n| :--- | :---: |\n")
        f.write(f"| Mean CER (all lines) | **{mean_cer:.3f}%** |\n")
        f.write(f"| Mean CER (ok lines only) | **{mean_cer_clean:.3f}%** |\n")
        f.write(f"| Median CER (all lines) | **{median_cer:.3f}%** |\n")
        if agg_bcer is not None:
            f.write(f"| lstmeval BCER (aggregate) | **{agg_bcer:.3f}%** |\n")
            f.write(f"| lstmeval BWER | **{agg_bwer:.3f}%** |\n")
        f.write("\n## Document-level Performance\n\n")
        f.write("| Document Page | Lines | Mean CER | Median CER |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for d in doc_stats:
            f.write(f"| `{d['doc_id']}` | {d['count']} | {d['mean_cer']:.2f}% | {d['median_cer']:.2f}% |\n")
        f.write("\n## Top 10 Worst Performing Lines\n\n")
        f.write("| Base Name | Document | CER | Status |\n")
        f.write("| :--- | :--- | :---: | :--- |\n")
        for r in sorted(results, key=lambda x: x["cer"], reverse=True)[:10]:
            f.write(f"| `{r['base_name']}` | `{r['doc_id']}` | {r['cer']:.2f}% | {r['status']} |\n")
    print(f"Saved report          → {report_path}")


if __name__ == "__main__":
    main()

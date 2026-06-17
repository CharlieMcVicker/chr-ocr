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
## ---------------------------------------------------------------------------
# Tesseract recognition & unicharset helpers
# ---------------------------------------------------------------------------

def convert_checkpoint_to_traineddata(checkpoint_path: str, traineddata_path: str, output_path: str):
    """Convert training checkpoint to a runtime traineddata file."""
    cmd = [
        "lstmtraining",
        "--stop_training",
        "--continue_from", checkpoint_path,
        "--traineddata", traineddata_path,
        "--model_output", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def get_allowed_characters(traineddata_path: str) -> set[str]:
    """Extract and parse unicharset from traineddata."""
    import tempfile
    allowed_chars = set()
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "extract.")
        cmd = ["combine_tessdata", "-u", traineddata_path, prefix]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            unicharset_path = prefix + "lstm-unicharset"
            if not os.path.exists(unicharset_path):
                unicharset_path = prefix + "unicharset"
            if os.path.exists(unicharset_path):
                with open(unicharset_path, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
                    if lines:
                        for line in lines[1:]:
                            parts = line.split()
                            if not parts:
                                continue
                            char = parts[0]
                            if char in ("NULL", "Joined", "|Broken|0|1"):
                                continue
                            match = re.search(r'#\s*(\S+)', line)
                            if match:
                                allowed_chars.add(match.group(1))
                            else:
                                allowed_chars.add(char)
    allowed_chars.update({" ", "\t", "\n", "\r"})
    return allowed_chars


def check_true_encoding_errors(truth: str, allowed_chars: set[str]) -> list[str]:
    """Return characters in truth not in allowed_chars."""
    return [c for c in truth if c not in allowed_chars]


def recognize_line(img_path: str, tessdata_dir: str, lang: str) -> str:
    """Run Tesseract in recognition mode on single line crop."""
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


def process_file_entry(entry: dict, allowed_chars: set[str], temp_tessdata_dir: str, temp_lang: str) -> dict:
    truth = entry["truth"]
    lstmf_path = entry["lstmf_path"]
    img_path = os.path.splitext(lstmf_path)[0] + ".png"
    
    invalid_chars = []
    status = "ok"
    matched_ocr = ""
    line_cer = 0.0
    
    if not truth:
        status = "no_gt"
        line_cer = 100.0
    else:
        invalid_chars = check_true_encoding_errors(truth, allowed_chars)
        if invalid_chars:
            status = "encoding_error"
            line_cer = 100.0
        else:
            if os.path.exists(img_path):
                matched_ocr = recognize_line(img_path, temp_tessdata_dir, temp_lang)
                line_cer = cer(truth, matched_ocr)
            else:
                status = "no_gt"
                line_cer = 100.0
                
    return {
        "file": lstmf_path,
        "base_name": entry["base_name"],
        "doc_id": entry["doc_id"],
        "line_id": entry["line_id"],
        "truth": truth,
        "ocr": matched_ocr,
        "cer": line_cer,
        "status": status,
        "invalid_chars": invalid_chars,
    }


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

    # 2. Convert checkpoint to a temporary traineddata file
    print("Converting checkpoint to a runtime traineddata file...")
    temp_traineddata = os.path.join(args.output_dir, "temp_eval.traineddata")
    temp_tessdata_dir = args.output_dir
    temp_lang = "temp_eval"
    
    try:
        convert_checkpoint_to_traineddata(args.checkpoint, args.traineddata, temp_traineddata)
        
        # 3. Extract unicharset to identify true encoding errors
        print("Extracting unicharset to determine allowed characters...")
        allowed_chars = get_allowed_characters(temp_traineddata)
        
        # 4. Load ground truths from disk
        print("Loading ground truth files from disk...")
        file_entries = load_ground_truths(lstmf_files)
        missing_gt = sum(1 for e in file_entries if not e["truth"])
        print(f"  {len(file_entries) - missing_gt} with GT text, {missing_gt} missing.")
        
        # 5. Run recognition in parallel on all image crops
        print("Running Tesseract recognition per line crop...")
        from functools import partial
        process_func = partial(process_file_entry, allowed_chars=allowed_chars, 
                               temp_tessdata_dir=temp_tessdata_dir, temp_lang=temp_lang)
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(process_func, file_entries))
            
    finally:
        # Clean up temporary traineddata file and any extracted components
        print("Cleaning up temporary evaluation assets...")
        for pattern in ["temp_eval.traineddata", "extract.*"]:
            for p in glob.glob(os.path.join(temp_tessdata_dir, pattern)):
                try:
                    os.remove(p)
                except Exception:
                    pass

    valid_results = [r for r in results if r["status"] == "ok"]
    ok_count = len(valid_results)
    err_count = len(results) - ok_count
    
    encoding_errors = [r for r in results if r["status"] == "encoding_error"]
    print(f"Assigned: {ok_count} ok, {err_count} encoding errors / missing GT (dropped from performance metrics).")
    if encoding_errors:
        print(f"  Detected {len(encoding_errors)} true encoding errors:")
        for r in encoding_errors:
            unique_invalid = sorted(list(set(r["invalid_chars"])))
            print(f"    - {r['base_name']}: missing characters {unique_invalid}")

    # 6. Aggregate stats (calculated ONLY on valid/encodeable lines)
    all_cers = [r["cer"] for r in valid_results]
    mean_cer = np.mean(all_cers) if all_cers else float("nan")
    median_cer = np.median(all_cers) if all_cers else float("nan")

    print(f"\nResults ({ok_count} valid lines, {err_count} dropped):")
    print(f"  Mean CER           : {mean_cer:.3f}%")
    print(f"  Median CER         : {median_cer:.3f}%")

    # 7. Document-level grouping (using valid results only)
    doc_groups: dict[str, list[float]] = {}
    for r in valid_results:
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
        f.write(f"- **Dataset**: `{args.test_dir}` ({len(results)} total lines, {ok_count} evaluated, {err_count} dropped)\n")
        f.write(f"- **Dropped (encoding errors / missing GT)**: {err_count} lines\n\n")
        f.write("## Overall Metrics (Evaluated Lines Only)\n\n")
        f.write("| Metric | Value |\n| :--- | :---: |\n")
        f.write(f"| Mean CER | **{mean_cer:.3f}%** |\n")
        f.write(f"| Median CER | **{median_cer:.3f}%** |\n")
        f.write("\n## Document-level Performance\n\n")
        f.write("| Document Page | Lines | Mean CER | Median CER |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for d in doc_stats:
            f.write(f"| `{d['doc_id']}` | {d['count']} | {d['mean_cer']:.2f}% | {d['median_cer']:.2f}% |\n")
        
        if encoding_errors:
            f.write("\n## Excluded True Encoding Errors\n\n")
            f.write("| Base Name | Missing Characters | Ground Truth |\n")
            f.write("| :--- | :---: | :--- |\n")
            for r in encoding_errors:
                unique_invalid = "".join(sorted(list(set(r["invalid_chars"]))))
                f.write(f"| `{r['base_name']}` | `{unique_invalid}` | `{r['truth']}` |\n")

        f.write("\n## Top 10 Worst Performing Lines\n\n")
        f.write("| Base Name | Document | CER | Status |\n")
        f.write("| :--- | :--- | :---: | :--- |\n")
        for r in sorted(valid_results, key=lambda x: x["cer"], reverse=True)[:10]:
            f.write(f"| `{r['base_name']}` | `{r['doc_id']}` | {r['cer']:.2f}% | {r['status']} |\n")
    print(f"Saved report          → {report_path}")


if __name__ == "__main__":
    main()

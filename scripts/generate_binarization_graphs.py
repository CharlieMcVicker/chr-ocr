#!/usr/bin/env python3
"""
generate_binarization_graphs.py

Evaluates a Tesseract OCR checkpoint against all binarization algorithm subdirectories
under a test root directory and produces:
  1. A summary bar chart comparing mean CER across all 30 algorithms.
  2. A compound bar chart showing CER per-file grouped by the worst performing lines,
     broken down by algorithm.
  3. A markdown comparative performance report.
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
    Pattern: YYYY-MM-DD_seq-N_col_CC_line_LLL[_augment].lstmf
    """
    filename = os.path.basename(filepath)
    base_name = os.path.splitext(filename)[0]
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
    Returns an ordered list of dicts.
    """
    entries = []
    for lstmf_path in lstmf_files:
        base = os.path.splitext(lstmf_path)[0]
        gt_path = base + ".gt.txt"
        doc_id, line_id, base_name = parse_filename_metadata(lstmf_path)
        truth = ""
        if os.path.exists(gt_path):
            try:
                with open(gt_path, "r", encoding="utf-8") as f:
                    truth = f.read().strip()
            except Exception:
                pass
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
    """Run lstmeval once; return stderr."""
    cmd = [
        "lstmeval",
        "--model", checkpoint_path,
        "--traineddata", traineddata_path,
        "--eval_listfile", list_file,
    ]
    print(f"Running evaluation: {' '.join(cmd)}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stderr


def parse_truth_ocr_pairs(lstmeval_output: str) -> list[tuple[str, str]]:
    """Extract (truth, ocr) pairs in order from lstmeval output."""
    pairs = []
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
    Match truth-ocr pairs to file entries. Files skipped by lstmeval
    due to encoding issues or missing GT default to CER = 100%.
    """
    from collections import defaultdict
    truth_to_indices = defaultdict(list)
    for idx, (truth, _) in enumerate(pairs):
        truth_to_indices[norm(truth)].append(idx)

    truth_ptr = {}
    results = []

    for entry in file_entries:
        norm_t = entry["norm_truth"]
        truth = entry["truth"]
        matched_ocr = None

        if norm_t and norm_t in truth_to_indices:
            indices = truth_to_indices[norm_t]
            ptr = truth_ptr.get(norm_t, 0)
            if ptr < len(indices):
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

def plot_summary_chart(algo_stats: list[dict], output_path: str):
    """Plot mean CER per algorithm, sorted ascending."""
    sorted_stats = sorted(algo_stats, key=lambda x: x["mean_cer"])
    names = [s["name"] for s in sorted_stats]
    means = [s["mean_cer"] for s in sorted_stats]

    fig, ax = plt.subplots(figsize=(12, 8))
    # Pick a vibrant palette
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(names)))
    bars = ax.barh(names, means, color=colors, edgecolor="black", height=0.7)

    ax.set_title("Mean Character Error Rate (CER) by Binarization Algorithm", fontsize=14, fontweight="bold")
    ax.set_xlabel("Mean CER (%)", fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    # Add text labels on the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.2, bar.get_y() + bar.get_height()/2, f"{width:.2f}%",
                va="center", ha="left", fontsize=9, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved summary chart   → {output_path}")


def plot_compound_chart(
    results_by_algo: dict[str, list[dict]],
    selected_files: list[str],
    algos: list[str],
    output_path: str
):
    """
    Plot a compound grouped bar chart showing CER per selected file for each binarization algorithm.
    """
    n_files = len(selected_files)
    n_algos = len(algos)

    fig, ax = plt.subplots(figsize=(16, 8))

    x = np.arange(n_files)
    width = 0.8 / n_algos  # width of each individual bar

    # Use a colormap to distinguish all algorithms
    cmap = plt.cm.get_cmap("gist_rainbow")

    file_to_idx = {f: idx for idx, f in enumerate(selected_files)}

    for idx, algo in enumerate(algos):
        cers = [100.0] * n_files
        for r in results_by_algo[algo]:
            base_name = r["base_name"]
            if base_name in file_to_idx:
                cers[file_to_idx[base_name]] = r["cer"]

        pos = x - 0.4 + (idx + 0.5) * width
        ax.bar(pos, cers, width=width, label=algo, color=cmap(idx / n_algos), edgecolor="none", alpha=0.9)

    ax.set_title(f"CER Comparison across Binarization Algorithms (Top {n_files} Worst Lines)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Document Line Name", fontsize=12)
    ax.set_ylabel("Character Error Rate (%)", fontsize=12)
    ax.set_xticks(x)
    short_labels = [f.replace("1828-", "") for f in selected_files]
    ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=9)
    ax.legend(title="Algorithm", bbox_to_anchor=(1.01, 1), loc="upper left", ncol=2, fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Saved compound chart  → {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate OCR model across all binarization subdirectories and plot comparisons."
    )
    parser.add_argument("--checkpoint",
        default="training_data/dataset_staged_output_full/chr_16.457_1987_2300.checkpoint")
    parser.add_argument("--test-root", default="training_data/dataset/test")
    parser.add_argument("--traineddata", default="training_data/dataset/model/chr.traineddata")
    parser.add_argument("--output-dir", default="training_data/performance_analysis")
    parser.add_argument("--top-n-worst", type=int, default=15,
        help="Number of worst-performing files to show in compound chart")
    args = parser.parse_args()

    for path, label in [
        (args.checkpoint, "checkpoint"),
        (args.test_root, "test root directory"),
        (args.traineddata, "traineddata"),
    ]:
        if not os.path.exists(path):
            print(f"Error: {label} not found at {path}")
            sys.exit(1)

    os.makedirs(args.output_dir, exist_ok=True)

    subdirs = sorted([
        d for d in glob.glob(os.path.join(args.test_root, "*/"))
        if os.path.isdir(d)
    ])
    if not subdirs:
        print(f"Error: No subdirectories found in test root: {args.test_root}")
        sys.exit(1)

    results_by_algo = {}
    algo_stats = []

    for subdir_path in subdirs:
        algo_name = os.path.basename(subdir_path.rstrip("/"))
        print(f"\nEvaluating binarization algorithm: {algo_name}")

        lstmf_files = sorted(glob.glob(os.path.join(subdir_path, "*.lstmf")))
        if not lstmf_files:
            print(f"  Warning: No .lstmf files found in {subdir_path}. Skipping.")
            continue

        file_entries = load_ground_truths(lstmf_files)

        list_file = os.path.join(subdir_path, "list.test")
        with open(list_file, "w", encoding="utf-8") as f:
            for p in lstmf_files:
                f.write(os.path.abspath(p) + "\n")

        lstmeval_output = run_lstmeval(args.checkpoint, args.traineddata, list_file)
        pairs = parse_truth_ocr_pairs(lstmeval_output)
        assigned = assign_pairs_to_files(pairs, file_entries)
        results_by_algo[algo_name] = assigned

        all_cers = [r["cer"] for r in assigned]
        mean_cer = np.mean(all_cers)
        median_cer = np.median(all_cers)
        ok_count = sum(1 for r in assigned if r["status"] == "ok")
        err_count = len(assigned) - ok_count

        algo_stats.append({
            "name": algo_name,
            "mean_cer": mean_cer,
            "median_cer": median_cer,
            "ok_count": ok_count,
            "err_count": err_count,
            "total_count": len(assigned),
        })
        print(f"  Mean CER: {mean_cer:.3f}%, OK: {ok_count}/{len(assigned)}, Errors/Skipped: {err_count}")

    if not algo_stats:
        print("Error: No data evaluated.")
        sys.exit(1)

    all_base_names = set()
    for assigned in results_by_algo.values():
        for r in assigned:
            all_base_names.add(r["base_name"])

    file_avg_cers = {}
    for base_name in all_base_names:
        cers = []
        for algo, assigned in results_by_algo.items():
            match = next((r for r in assigned if r["base_name"] == base_name), None)
            if match:
                cers.append(match["cer"])
            else:
                cers.append(100.0)
        file_avg_cers[base_name] = np.mean(cers)

    sorted_worst_files = sorted(file_avg_cers.keys(), key=lambda k: file_avg_cers[k], reverse=True)
    selected_worst_files = sorted_worst_files[:args.top_n_worst]

    plot_summary_chart(algo_stats, os.path.join(args.output_dir, "binarization_summary.png"))

    sorted_algo_names = [s["name"] for s in sorted(algo_stats, key=lambda x: x["mean_cer"])]
    plot_compound_chart(
        results_by_algo,
        selected_worst_files,
        sorted_algo_names,
        os.path.join(args.output_dir, "binarization_compound_by_file.png")
    )

    report_path = os.path.join(args.output_dir, "binarization_performance_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Binarization Algorithm Performance Comparison Report\n\n")
        f.write(f"- **Checkpoint**: `{args.checkpoint}`\n")
        f.write(f"- **Test Root Directory**: `{args.test_root}`\n")
        f.write(f"- **Number of Algorithms evaluated**: {len(algo_stats)}\n\n")

        f.write("## Overall Metrics by Algorithm\n\n")
        f.write("Sorted from lowest mean Character Error Rate (best) to highest.\n\n")
        f.write("| Rank | Binarization Algorithm | Mean CER | Median CER | OK Lines | Error/Skipped |\n")
        f.write("| :---: | :--- | :---: | :---: | :---: | :---: |\n")
        for rank, s in enumerate(sorted(algo_stats, key=lambda x: x["mean_cer"]), 1):
            f.write(f"| {rank} | `{s['name']}` | **{s['mean_cer']:.3f}%** | {s['median_cer']:.3f}% | {s['ok_count']}/{s['total_count']} | {s['err_count']} |\n")

        f.write(f"\n## Top {args.top_n_worst} Worst-Performing Lines (Average across all algorithms)\n\n")
        f.write("| Rank | Base Name | Average CER | " + " | ".join(f"`{name}`" for name in sorted_algo_names[:5]) + " | ... |\n")
        f.write("| :---: | :--- | :---: | " + " | ".join(":---:" for _ in range(5)) + " | :---: |\n")

        for rank, base_name in enumerate(selected_worst_files, 1):
            avg_val = file_avg_cers[base_name]
            cols = []
            for name in sorted_algo_names[:5]:
                match = next((r for r in results_by_algo[name] if r["base_name"] == base_name), None)
                val_str = f"{match['cer']:.1f}%" if match else "N/A"
                cols.append(val_str)
            f.write(f"| {rank} | `{base_name}` | **{avg_val:.2f}%** | " + " | ".join(cols) + " | ... |\n")

    print(f"Saved report          → {report_path}")


if __name__ == "__main__":
    main()

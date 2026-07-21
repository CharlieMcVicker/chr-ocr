#!/usr/bin/env python3
"""
generate_column_confidence_histogram.py

Loads OCR results from manifest_w_lang.json, filters for Cherokee items,
groups lines by column (source_scan, column_index), calculates the mean OCR confidence
for each column, and plots a beautiful distribution histogram.
Saves the visualization to training_data/performance_analysis/column_confidence_histogram.png.
"""

import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

def main():
    manifest_path = "training_data/manifest_w_lang.json"
    output_dir = "training_data/performance_analysis"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(manifest_path):
        print(f"Error: {manifest_path} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading manifest from {manifest_path}...")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Group confidences by column (source_scan, column_index)
    columns_data = {}
    for item_id, item in manifest.items():
        scan = item.get("source_scan")
        col_idx = item.get("column_index")
        confidence = item.get("ftm_confidence")
        predicted_lang = item.get("predicted_lang")

        # Only process Cherokee items with valid scan, col_idx, and non-zero confidence score
        if predicted_lang == "Cherokee" and scan and col_idx is not None and confidence is not None and confidence > 0.0:
            column_key = (scan, col_idx)
            if column_key not in columns_data:
                columns_data[column_key] = []
            columns_data[column_key].append(confidence)

    # Calculate mean confidence for each unique column
    mean_confidences = []
    for key, confs in columns_data.items():
        if confs:
            mean_confidences.append(sum(confs) / len(confs))

    if not mean_confidences:
        print("Error: No valid Cherokee column confidence data found in manifest.")
        sys.exit(1)

    print(f"Found {len(mean_confidences)} columns with valid Cherokee OCR data.")
    overall_mean = np.mean(mean_confidences)
    overall_median = np.median(mean_confidences)
    print(f"Overall Mean Column OCR Confidence: {overall_mean:.2f}%")
    print(f"Overall Median Column OCR Confidence: {overall_median:.2f}%")

    # Setup premium font/styling
    plt.rcParams['font.sans-serif'] = ['Inter', 'Outfit', 'DejaVu Sans', 'Arial', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # Custom teal/indigo gradient coloring for the histogram bars
    n_bins = 20
    counts, bins, patches = ax.hist(
        mean_confidences,
        bins=n_bins,
        range=(50, 100),
        color="#1f77b4",
        edgecolor="#ffffff",
        linewidth=1.2,
        alpha=0.85
    )

    # Gradient coloring based on bin value (higher confidence gets richer/deeper teal colors)
    cm = plt.colormaps["viridis"]
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    # normalize bin centers for colormap
    col_norm = plt.Normalize(50, 100)
    for c, p in zip(bin_centers, patches):
        plt.setp(p, 'facecolor', cm(col_norm(c)))

    # Add labels and premium title
    ax.set_title("Distribution of Mean OCR Confidence per Column", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Mean OCR Confidence (%)", fontsize=12, fontweight="semibold", labelpad=10)
    ax.set_ylabel("Number of Columns (Count)", fontsize=12, fontweight="semibold", labelpad=10)

    # Add mean and median vertical indicator lines
    ax.axvline(overall_mean, color="#e74c3c", linestyle="--", linewidth=1.5, label=f"Mean: {overall_mean:.1f}%")
    ax.axvline(overall_median, color="#2ecc71", linestyle=":", linewidth=1.5, label=f"Median: {overall_median:.1f}%")

    # Clean up axes/spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.grid(axis="y", linestyle="--", alpha=0.4, color="#aaaaaa")
    ax.set_axisbelow(True)

    # Add legend
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cccccc", fontsize=10, loc="upper left")

    # Layout adjustment and save
    output_png = os.path.join(output_dir, "column_confidence_histogram.png")
    plt.tight_layout()
    plt.savefig(output_png, bbox_inches="tight", dpi=300)
    plt.close(fig)

    print(f"Successfully generated histogram! Saved to: {output_png}")

if __name__ == "__main__":
    main()

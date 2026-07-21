#!/usr/bin/env python3
"""
visualize_confusion.py

Loads the generated confusion matrix CSV, extracts the top 20 most frequent
character-level substitution errors, and visualizes them using matplotlib.
Saves the visualization as a premium PNG image.
"""

import os
import csv
import sys
import matplotlib.pyplot as plt

def main():
    csv_path = "training_data/performance_analysis/confusion_matrix.csv"
    output_png = "training_data/performance_analysis/top_20_confusions.png"

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} does not exist. Please run generate_confusion_matrix.py first.")
        sys.exit(1)

    # Parse confusion matrix CSV
    confusions = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        cols = header[1:-1] # exclude row title and '<del>'
        
        for row in reader:
            truth = row[0]
            if truth == "" or truth == "Truth \\ Predicted":
                continue
            
            # Row values corresponding to predicted cols
            for col_idx, col_name in enumerate(cols):
                pred = col_name
                if truth == pred:
                    continue
                try:
                    count = int(row[col_idx + 1])
                    if count > 0:
                        confusions.append((truth, pred, count))
                except ValueError:
                    continue

    # Sort confusions by count in descending order
    confusions.sort(key=lambda x: x[2], reverse=True)
    top_20 = confusions[:20]

    if not top_20:
        print("No confusions found to visualize.")
        sys.exit(0)

    # Reverse for plotting top-down in horizontal bar chart
    top_20.reverse()

    labels = [f"'{t}' -> '{p}'" for t, p, _ in top_20]
    counts = [count for _, _, count in top_20]

    # Setup premium styling
    plt.rcParams['font.sans-serif'] = ['Plantagenet Cherokee', 'Noto Sans Cherokee', 'Arial', 'DejaVu Sans', 'sans-serif']
    plt.rcParams['font.family'] = 'sans-serif'
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    
    # Create subtle gradient-like color list (sleek purples/blues)
    colors = plt.cm.plasma(range(50, 250, 10))[:20]
    
    bars = ax.barh(labels, counts, color=colors, edgecolor='none', height=0.6)
    
    # Add counts to the end of each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + max(counts)*0.01, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', va='center', fontsize=10, fontweight='bold', color='#333333')

    # Styling labels and title
    ax.set_title("Top 20 Cherokee Character OCR Confusions", fontsize=16, fontweight='bold', pad=20, color='#111111')
    ax.set_xlabel("Confusion Count (Number of Occurrences)", fontsize=12, labelpad=12, fontweight='semibold', color='#333333')
    ax.set_ylabel("Substitution Pair (Truth -> Predicted)", fontsize=12, labelpad=12, fontweight='semibold', color='#333333')
    
    # Clean up grid and spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.grid(axis='x', linestyle='--', alpha=0.5, color='#aaaaaa')
    ax.set_axisbelow(True)
    
    # Tick formatting
    ax.tick_params(colors='#333333', labelsize=11)
    
    plt.tight_layout()
    plt.savefig(output_png, bbox_inches='tight')
    print(f"Visualization successfully saved to {output_png}")

if __name__ == "__main__":
    main()

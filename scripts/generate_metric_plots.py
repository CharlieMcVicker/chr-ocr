#!/usr/bin/env python3
"""
generate_metric_plots.py

Generates premium, high-resolution performance plots from training run metrics CSVs:
  - iteration_metrics.csv (loss, BCER, BWER, skip ratio)
  - epoch_metrics.csv (Phoenix CER, CNT CER, Weighted CER)

Supports:
  1. Single Run Mode: Generates consolidated plots and saves them to the run directory.
  2. Comparison Mode: Compares multiple runs side-by-side on the same graphs.
"""

import os
import re
import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# Professional aesthetic settings
plt.style.use('dark_background')
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'grid.color': '#333333',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'axes.edgecolor': '#444444',
    'axes.linewidth': 1.0,
})

def find_run_dir(run_identifier):
    """
    Finds the run directory based on an absolute/relative path or a name inside common directories.
    """
    if os.path.isdir(run_identifier):
        return run_identifier
    
    search_paths = [
        run_identifier,
        os.path.join("training_data", run_identifier),
        os.path.join("training_data", "staged_tuning", run_identifier),
        os.path.join("training_data", "staged_tuning", f"{run_identifier}_output")
    ]
    
    for path in search_paths:
        if os.path.isdir(path):
            return path
            
    print(f"Error: Could not resolve run directory for: '{run_identifier}'", file=sys.stderr)
    return None

def load_metrics(run_dir):
    """
    Loads iteration and epoch metrics from a run directory, normalising column headers.
    """
    iter_path = os.path.join(run_dir, "iteration_metrics.csv")
    epoch_path = os.path.join(run_dir, "epoch_metrics.csv")
    
    iter_df = None
    epoch_df = None
    
    if os.path.exists(iter_path):
        try:
            iter_df = pd.read_csv(iter_path)
            # Normalize casing
            iter_df.columns = [c.lower() for c in iter_df.columns]
            if "mean_rms" in iter_df.columns and "train_loss" not in iter_df.columns:
                iter_df["train_loss"] = iter_df["mean_rms"]
        except Exception as e:
            print(f"Warning: Failed to load {iter_path}: {e}", file=sys.stderr)
            
    if os.path.exists(epoch_path):
        try:
            epoch_df = pd.read_csv(epoch_path)
            # Normalize casing
            epoch_df.columns = [c.lower() for c in epoch_df.columns]
        except Exception as e:
            print(f"Warning: Failed to load {epoch_path}: {e}", file=sys.stderr)
            
    return iter_df, epoch_df

def plot_single_run(run_dir, output_dir=None):
    """
    Generates beautiful plots for a single run and saves them to disk.
    """
    run_name = os.path.basename(os.path.normpath(run_dir))
    iter_df, epoch_df = load_metrics(run_dir)
    
    if iter_df is None and epoch_df is None:
        print(f"Error: No valid metrics files found in {run_dir}", file=sys.stderr)
        return
    
    dest_dir = output_dir if output_dir else run_dir
    os.makedirs(dest_dir, exist_ok=True)
    
    # Define color palette
    colors = {
        'loss': '#f59e0b',       # Amber
        'bcer': '#3b82f6',       # Bright Blue
        'bwer': '#10b981',       # Emerald Mint
        'phoenix': '#60a5fa',    # Light Blue
        'cnt': '#f43f5e',        # Rose
        'weighted': '#8b5cf6'    # Purple
    }
    
    # 1. Iteration Metrics Plot
    if iter_df is not None and not iter_df.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle(f"Iteration Telemetry - {run_name}", y=0.98)
        
        # Loss / RMS
        if "train_loss" in iter_df.columns:
            ax1.plot(iter_df["iteration"], iter_df["train_loss"], color=colors['loss'], linewidth=1.5, label="Train Loss (RMS)")
            ax1.set_ylabel("Loss / RMS Error")
            ax1.set_xlabel("Iteration")
            ax1.set_title("Training Loss Convergence")
            ax1.grid(True)
            ax1.legend()
            
        # BCER / BWER
        has_bcer = "bcer_train" in iter_df.columns
        has_bwer = "bwer_train" in iter_df.columns
        if has_bcer or has_bwer:
            if has_bcer:
                ax2.plot(iter_df["iteration"], iter_df["bcer_train"], color=colors['bcer'], linewidth=1.5, label="BCER (Char Error)")
            if has_bwer:
                ax2.plot(iter_df["iteration"], iter_df["bwer_train"], color=colors['bwer'], linewidth=1.5, label="BWER (Word Error)")
            ax2.set_ylabel("Error Rate (%)")
            ax2.set_xlabel("Iteration")
            ax2.set_title("Training Error Rates")
            ax2.grid(True)
            ax2.legend()
            
        plt.tight_layout()
        out_path = os.path.join(dest_dir, "iteration_metrics.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Generated: {out_path}")
        
    # 2. Epoch Metrics Plot
    if epoch_df is not None and not epoch_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle(f"Epoch Validation CER - {run_name}", y=0.98)
        
        x_col = "epoch" if "epoch" in epoch_df.columns else "iteration" if "iteration" in epoch_df.columns else None
        
        if x_col:
            # We want to check for lowercase normalised names
            if "phoenix_cer" in epoch_df.columns:
                ax.plot(epoch_df[x_col], epoch_df["phoenix_cer"], color=colors['phoenix'], marker='o', linewidth=2, label="Phoenix CER")
            if "cnt_cer" in epoch_df.columns:
                ax.plot(epoch_df[x_col], epoch_df["cnt_cer"], color=colors['cnt'], marker='s', linewidth=2, label="CNT CER")
            if "weighted_cer" in epoch_df.columns:
                ax.plot(epoch_df[x_col], epoch_df["weighted_cer"], color=colors['weighted'], marker='^', linewidth=2, label="Weighted CER")
                
            ax.set_ylabel("Character Error Rate (CER %)")
            ax.set_xlabel(x_col.capitalize())
            ax.set_title("Evaluation Performance by Checkpoint")
            ax.grid(True)
            ax.legend()
            
            plt.tight_layout()
            out_path = os.path.join(dest_dir, "epoch_metrics.png")
            plt.savefig(out_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Generated: {out_path}")

def plot_comparison(run_dirs, output_path):
    """
    Compares multiple runs on the same set of graphs and saves the output.
    """
    # Load all run data
    runs_data = []
    for r_dir in run_dirs:
        run_name = os.path.basename(os.path.normpath(r_dir))
        iter_df, epoch_df = load_metrics(r_dir)
        runs_data.append({
            'name': run_name,
            'iter': iter_df,
            'epoch': epoch_df
        })
        
    # We will create a combined figure with multiple subplots to compare key metrics
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle("OCR Training & Evaluation Run Comparison", y=0.98, fontsize=18)
    
    # 1. Compare Training Loss (top-left)
    ax_loss = axes[0, 0]
    ax_loss.set_title("Training Loss (RMS)")
    ax_loss.set_xlabel("Iteration")
    ax_loss.set_ylabel("Loss")
    ax_loss.grid(True)
    
    # 2. Compare Training BCER (top-right)
    ax_bcer = axes[0, 1]
    ax_bcer.set_title("Training Character Error Rate (BCER)")
    ax_bcer.set_xlabel("Iteration")
    ax_bcer.set_ylabel("BCER (%)")
    ax_bcer.grid(True)
    
    # 3. Compare Phoenix Validation CER (bottom-left)
    ax_phoenix = axes[1, 0]
    ax_phoenix.set_title("Validation Phoenix CER")
    ax_phoenix.set_xlabel("Epoch / Evaluation Step")
    ax_phoenix.set_ylabel("CER (%)")
    ax_phoenix.grid(True)
    
    # 4. Compare Weighted Validation CER (bottom-right)
    ax_weighted = axes[1, 1]
    ax_weighted.set_title("Validation Weighted CER")
    ax_weighted.set_xlabel("Epoch / Evaluation Step")
    ax_weighted.set_ylabel("Weighted CER (%)")
    ax_weighted.grid(True)
    
    # Plot each run
    for run in runs_data:
        name = run['name']
        iter_df = run['iter']
        epoch_df = run['epoch']
        
        # Plot iteration level metrics
        if iter_df is not None and not iter_df.empty:
            if "iteration" in iter_df.columns:
                if "train_loss" in iter_df.columns:
                    ax_loss.plot(iter_df["iteration"], iter_df["train_loss"], label=name, linewidth=1.5)
                if "bcer_train" in iter_df.columns:
                    ax_bcer.plot(iter_df["iteration"], iter_df["bcer_train"], label=name, linewidth=1.5)
                    
        # Plot epoch level metrics
        if epoch_df is not None and not epoch_df.empty:
            x_col = "epoch" if "epoch" in epoch_df.columns else "iteration" if "iteration" in epoch_df.columns else None
            if x_col:
                if "phoenix_cer" in epoch_df.columns:
                    ax_phoenix.plot(epoch_df[x_col], epoch_df["phoenix_cer"], marker='o', label=name, linewidth=2)
                if "weighted_cer" in epoch_df.columns:
                    ax_weighted.plot(epoch_df[x_col], epoch_df["weighted_cer"], marker='^', label=name, linewidth=2)

    # Add legends
    ax_loss.legend()
    ax_bcer.legend()
    ax_phoenix.legend()
    ax_weighted.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated Comparison Plot: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate premium performance/metrics plots from training runs.")
    parser.add_argument("--run-dir", help="Single run directory or name to plot.")
    parser.add_argument("--compare", nargs="+", help="Compare multiple run directories or names.")
    parser.add_argument("--output-dir", help="Optional output directory for single run plots.")
    parser.add_argument("--output-file", default="training_data/run_comparison.png", help="Output path for comparison plot.")
    
    args = parser.parse_args()
    
    if args.compare:
        resolved_dirs = []
        for r in args.compare:
            resolved = find_run_dir(r)
            if resolved:
                resolved_dirs.append(resolved)
        if not resolved_dirs:
            print("Error: No valid comparison runs resolved.", file=sys.stderr)
            sys.exit(1)
        plot_comparison(resolved_dirs, args.output_file)
    elif args.run_dir:
        resolved = find_run_dir(args.run_dir)
        if resolved:
            plot_single_run(resolved, args.output_dir)
        else:
            sys.exit(1)
    else:
        # Default to discovering the latest runs or printing usage
        print("Please specify a run directory with --run-dir, or comparison runs with --compare.")
        parser.print_help()

if __name__ == "__main__":
    main()

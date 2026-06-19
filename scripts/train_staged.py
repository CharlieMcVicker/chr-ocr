#!/usr/bin/env python3
"""
Staged Epoch Loop supervisor script for dynamic augmentation generation and Tesseract model training.
Orchestrates Tesseract training epoch-by-epoch while maintaining a low disk footprint.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.config import TrainingConfig
from phoenix.training.train import run_staged_training, get_latest_checkpoint
import shutil
import subprocess
import re
import json

def evaluate_and_update_best(config, config_path, top_n=5):
    """
    Locates the top N checkpoints of the run, converts them to .traineddata,
    evaluates them on Phoenix and CNT test splits, finds the best performing
    checkpoints of the run (separately for Phoenix CER and Weighted CER),
    and updates the respective best model directories if they outperform the global bests.
    """
    from phoenix.training.eval import get_sorted_checkpoints, compile_checkpoint, evaluate_checkpoint, track_and_update_bests
    
    checkpoints = get_sorted_checkpoints(config.train_output_dir, f"[-{top_n}:]")
    if not checkpoints:
        print(f"No checkpoints found in {config.train_output_dir} to evaluate.")
        return

    print(f"\nEvaluating the last {len(checkpoints)} epochs/checkpoints for run peak performers...")

    best_run_phoenix_metrics = None
    best_run_phoenix_cp = None
    min_run_phoenix_cer = float("inf")
    temp_best_phoenix_traineddata = None

    best_run_weighted_metrics = None
    best_run_weighted_cp = None
    min_run_weighted_cer = float("inf")
    temp_best_weighted_traineddata = None

    # Base traineddata for stop_training
    traineddata_path = os.path.join(config.model_dir, "chr.traineddata")
    if not os.path.exists(traineddata_path):
        print(f"Base traineddata not found at {traineddata_path}.")
        return

    for idx, checkpoint in enumerate(checkpoints, 1):
        print(f"\n[{idx}/{len(checkpoints)}] Compiling & evaluating checkpoint: {checkpoint}")

        # Unique temp path for this checkpoint's compiled traineddata
        temp_traineddata = os.path.join(config.train_output_dir, f"chr_eval_temp_{idx}.traineddata")
        
        if not compile_checkpoint(checkpoint, traineddata_path, temp_traineddata):
            continue

        metrics = evaluate_checkpoint(checkpoint, traineddata_path, config.train_output_dir, f"chr_eval_temp_{idx}")
        if not metrics:
            if os.path.exists(temp_traineddata):
                os.remove(temp_traineddata)
            continue

        # Print raw stats cleanly
        print(f"  Phoenix CER:  {metrics['phoenix_CER']}%  (WER: {metrics['phoenix_WER']}%)")
        print(f"  CNT CER:      {metrics['cnt_CER']}%  (WER: {metrics['cnt_WER']}%)")
        print(f"  Weighted CER: {metrics['weighted_CER']}%  (WER: {metrics['weighted_WER']}%)")

        # Check Phoenix CER best
        p_cer = metrics["phoenix_CER"]
        if p_cer is not None and p_cer < min_run_phoenix_cer:
            # Clean up old temp best phoenix traineddata
            if temp_best_phoenix_traineddata and os.path.exists(temp_best_phoenix_traineddata):
                os.remove(temp_best_phoenix_traineddata)
            
            min_run_phoenix_cer = p_cer
            best_run_phoenix_metrics = metrics
            best_run_phoenix_cp = checkpoint
            # Rename/keep this compiled traineddata as our temp best phoenix
            best_phoenix_path = os.path.join(config.train_output_dir, "chr_best_phoenix_temp.traineddata")
            if os.path.exists(best_phoenix_path):
                os.remove(best_phoenix_path)
            shutil.copy2(temp_traineddata, best_phoenix_path)
            temp_best_phoenix_traineddata = best_phoenix_path

        # Check Weighted CER best
        w_cer = metrics["weighted_CER"]
        if w_cer is not None and w_cer < min_run_weighted_cer:
            # Clean up old temp best weighted traineddata
            if temp_best_weighted_traineddata and os.path.exists(temp_best_weighted_traineddata):
                os.remove(temp_best_weighted_traineddata)
            
            min_run_weighted_cer = w_cer
            best_run_weighted_metrics = metrics
            best_run_weighted_cp = checkpoint
            # Rename/keep this compiled traineddata as our temp best weighted
            best_weighted_path = os.path.join(config.train_output_dir, "chr_best_weighted_temp.traineddata")
            if os.path.exists(best_weighted_path):
                os.remove(best_weighted_path)
            shutil.copy2(temp_traineddata, best_weighted_path)
            temp_best_weighted_traineddata = best_weighted_path

        # Remove the temp_traineddata as we have kept copies of the best performers
        if os.path.exists(temp_traineddata):
            os.remove(temp_traineddata)

    # 1. Update Best Phoenix Model
    if best_run_phoenix_metrics:
        print(f"\n==================================================")
        print(f"Peak Phoenix CER Performer of this Run: {best_run_phoenix_cp}")
        print(f"Phoenix CER: {min_run_phoenix_cer}%")
        print(f"==================================================")
        track_and_update_bests(
            best_run_phoenix_cp,
            best_run_phoenix_metrics,
            config_path,
            best_dir="best_model",
            temp_traineddata=temp_best_phoenix_traineddata
        )
        if temp_best_phoenix_traineddata and os.path.exists(temp_best_phoenix_traineddata):
            os.remove(temp_best_phoenix_traineddata)

    # 2. Update Best Weighted Model
    if best_run_weighted_metrics:
        print(f"\n==================================================")
        print(f"Peak Weighted CER Performer of this Run: {best_run_weighted_cp}")
        print(f"Weighted CER: {min_run_weighted_cer}%")
        print(f"==================================================")
        track_and_update_bests(
            best_run_weighted_cp,
            best_run_weighted_metrics,
            config_path,
            best_dir="best_model",
            temp_traineddata=temp_best_weighted_traineddata
        )
        if temp_best_weighted_traineddata and os.path.exists(temp_best_weighted_traineddata):
            os.remove(temp_best_weighted_traineddata)

def main():
    parser = argparse.ArgumentParser(description="Staged Epoch Loop for Tesseract OCR Fine-tuning (JSON Config Enforced)")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file (strictly required)")
    args = parser.parse_args()

    print(f"Loading configuration from JSON: {args.config}")
    config = TrainingConfig.load_from_json(args.config)

    run_staged_training(config)
    evaluate_and_update_best(config, args.config)

if __name__ == "__main__":
    main()

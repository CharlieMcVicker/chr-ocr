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

def evaluate_and_update_best(config, config_path):
    """
    Locates the final checkpoint of the run, converts it to .traineddata,
    evaluates it on Phoenix and CNT test splits, and updates the best model
    directory at the project root if it outperforms the previous best.
    """
    checkpoint = get_latest_checkpoint(config.train_output_dir)
    if not checkpoint or not os.path.exists(checkpoint):
        print(f"No checkpoint found in {config.train_output_dir} to evaluate.")
        return

    print(f"\nEvaluating final checkpoint of the run: {checkpoint}")

    # Extract .traineddata from checkpoint
    traineddata_path = os.path.join(config.model_dir, "chr.traineddata")
    if not os.path.exists(traineddata_path):
        print(f"Base traineddata not found at {traineddata_path}.")
        return

    temp_traineddata = os.path.join(config.train_output_dir, "chr_eval_temp.traineddata")
    if os.path.exists(temp_traineddata):
        try:
            os.remove(temp_traineddata)
        except Exception:
            pass

    unpack_cmd = [
        "lstmtraining",
        "--stop_training",
        "--continue_from", checkpoint,
        "--traineddata", traineddata_path,
        "--model_output", temp_traineddata
    ]
    try:
        subprocess.run(unpack_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        print(f"Failed to unpack checkpoint to traineddata: {e}")
        return

    # Run evaluate_mixed_model.py
    eval_cmd = [
        sys.executable,
        "scripts/evaluate_mixed_model.py",
        "--model-dir", config.train_output_dir,
        "--lang", "chr_eval_temp"
    ]
    try:
        res = subprocess.run(eval_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except Exception as e:
        print(f"Failed to run evaluate_mixed_model.py: {e}")
        if os.path.exists(temp_traineddata):
            os.remove(temp_traineddata)
        return

    eval_stdout = res.stdout
    print(eval_stdout)

    # Parse performance metrics
    phx_cer, phx_wer = None, None
    cnt_cer, cnt_wer = None, None
    weighted_cer, weighted_wer = None, None

    phx_match = re.search(r"Phoenix Test Set \(\d+ lines\):\s+Mean CER:\s+([\d\.]+)%\s+Mean WER:\s+([\d\.]+)%", eval_stdout)
    if phx_match:
        phx_cer = float(phx_match.group(1))
        phx_wer = float(phx_match.group(2))
        
    cnt_match = re.search(r"CNT Test Set \(\d+ lines\):\s+Mean CER:\s+([\d\.]+)%\s+Mean WER:\s+([\d\.]+)%", eval_stdout)
    if cnt_match:
        cnt_cer = float(cnt_match.group(1))
        cnt_wer = float(cnt_match.group(2))
        
    weighted_match = re.search(r"Overall Combined Weighted Performance \(\d+ lines total\):\s+Weighted Mean CER:\s+([\d\.]+)%\s+Weighted Mean WER:\s+([\d\.]+)%", eval_stdout)
    if weighted_match:
        weighted_cer = float(weighted_match.group(1))
        weighted_wer = float(weighted_match.group(2))

    if weighted_cer is None:
        print("Could not parse Weighted Mean CER from evaluation output.")
        if os.path.exists(temp_traineddata):
            os.remove(temp_traineddata)
        return

    stats = {
        "phoenix_CER": phx_cer,
        "phoenix_WER": phx_wer,
        "cnt_CER": cnt_cer,
        "cnt_WER": cnt_wer,
        "weighted_CER": weighted_cer,
        "weighted_WER": weighted_wer,
        "checkpoint_path": checkpoint
    }

    # Determine if we should update best_model folder at project root
    best_dir = "best_model"
    os.makedirs(best_dir, exist_ok=True)
    stats_path = os.path.join(best_dir, "scoring_stats.json")

    should_update = False
    if not os.path.exists(stats_path):
        print("No previous best model found. Saving this model as the first best model.")
        should_update = True
    else:
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                prev_stats = json.load(f)
            prev_cer = prev_stats.get("weighted_CER")
            if prev_cer is None or weighted_cer < prev_cer:
                print(f"New best model found! Weighted CER improved from {prev_cer}% to {weighted_cer}%.")
                should_update = True
            else:
                print(f"Model evaluated (Weighted CER: {weighted_cer}%). Previous best (Weighted CER: {prev_cer}%) remains best.")
        except Exception as e:
            print(f"Error reading previous stats, overwriting: {e}")
            should_update = True

    if should_update:
        # Copy checkpoint
        shutil.copy2(checkpoint, os.path.join(best_dir, "best.checkpoint"))
        # Copy config
        shutil.copy2(config_path, os.path.join(best_dir, "best_config.json"))
        # Copy compiled traineddata
        shutil.copy2(temp_traineddata, os.path.join(best_dir, "best.traineddata"))
        # Write stats
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"Updated best model files in {best_dir}/")

    # Clean up temporary traineddata
    if os.path.exists(temp_traineddata):
        os.remove(temp_traineddata)

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

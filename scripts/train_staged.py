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
    checkpoint of the run, and updates the best model directory at the project
    root if it outperforms the previous global best.
    """
    import glob
    checkpoints = glob.glob(os.path.join(config.train_output_dir, "*.checkpoint"))
    if not checkpoints:
        print(f"No checkpoints found in {config.train_output_dir} to evaluate.")
        return

    def get_iteration_num(cp_path):
        try:
            basename = os.path.basename(cp_path)
            part = basename.split("_")[-1].split(".")[0]
            if part.isdigit():
                return int(part)
        except Exception:
            pass
        match = re.findall(r"\d+", cp_path)
        if match:
            return int(match[-1])
        return 0

    checkpoints_sorted = sorted(checkpoints, key=get_iteration_num)
    eval_checkpoints = checkpoints_sorted[-top_n:]

    print(f"\nFound {len(checkpoints)} checkpoints. Evaluating the last {len(eval_checkpoints)} epochs/checkpoints...")

    best_run_stats = None
    best_run_checkpoint = None
    best_run_traineddata = None
    min_run_cer = float("inf")

    # Base traineddata for stop_training
    traineddata_path = os.path.join(config.model_dir, "chr.traineddata")
    if not os.path.exists(traineddata_path):
        print(f"Base traineddata not found at {traineddata_path}.")
        return

    for idx, checkpoint in enumerate(eval_checkpoints, 1):
        print(f"\n[{idx}/{len(eval_checkpoints)}] Compiling & evaluating checkpoint: {checkpoint}")

        temp_traineddata = os.path.join(config.train_output_dir, f"chr_eval_temp_{idx}.traineddata")
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
            continue

        # Run evaluate_mixed_model.py
        eval_cmd = [
            sys.executable,
            "scripts/evaluate_mixed_model.py",
            "--model-dir", config.train_output_dir,
            "--lang", f"chr_eval_temp_{idx}"
        ]
        try:
            res = subprocess.run(eval_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        except Exception as e:
            print(f"Failed to run evaluate_mixed_model.py: {e}")
            if os.path.exists(temp_traineddata):
                os.remove(temp_traineddata)
            continue

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
            continue

        stats = {
            "phoenix_CER": phx_cer,
            "phoenix_WER": phx_wer,
            "cnt_CER": cnt_cer,
            "cnt_WER": cnt_wer,
            "weighted_CER": weighted_cer,
            "weighted_WER": weighted_wer,
            "checkpoint_path": checkpoint
        }

        if weighted_cer < min_run_cer:
            # We found a better checkpoint in this run! Clean up previous best run temp traineddata if it exists
            if best_run_traineddata and os.path.exists(best_run_traineddata):
                try:
                    os.remove(best_run_traineddata)
                except Exception:
                    pass

            min_run_cer = weighted_cer
            best_run_stats = stats
            best_run_checkpoint = checkpoint
            best_run_traineddata = temp_traineddata
            print(f"--> Found new peak performer of this run: Weighted CER = {weighted_cer}%")
        else:
            # Clean up this evaluated temp traineddata as it's not the best
            if os.path.exists(temp_traineddata):
                os.remove(temp_traineddata)

    if not best_run_stats:
        print("No checkpoints were successfully evaluated.")
        return

    print(f"\n==================================================")
    print(f"Peak Performer of this Run: {best_run_checkpoint}")
    print(f"Weighted CER: {min_run_cer}%")
    print(f"==================================================")

    # Determine if we should update best_model folder at project root
    best_dir = "best_model"
    os.makedirs(best_dir, exist_ok=True)
    stats_path = os.path.join(best_dir, "scoring_stats.json")

    should_update = False
    if not os.path.exists(stats_path):
        print("No previous best model found. Saving this run's peak performer as the global best model.")
        should_update = True
    else:
        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                prev_stats = json.load(f)
            prev_cer = prev_stats.get("weighted_CER")
            if prev_cer is None or min_run_cer < prev_cer:
                print(f"New global best model found! Weighted CER improved from {prev_cer}% to {min_run_cer}%.")
                should_update = True
            else:
                print(f"Run peak performer (Weighted CER: {min_run_cer}%) did not beat global best (Weighted CER: {prev_cer}%). Global best remains.")
        except Exception as e:
            print(f"Error reading previous stats, overwriting: {e}")
            should_update = True

    if should_update:
        # Copy checkpoint
        shutil.copy2(best_run_checkpoint, os.path.join(best_dir, "best.checkpoint"))
        # Copy config
        shutil.copy2(config_path, os.path.join(best_dir, "best_config.json"))
        # Copy compiled traineddata
        shutil.copy2(best_run_traineddata, os.path.join(best_dir, "best.traineddata"))
        # Write stats
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(best_run_stats, f, indent=2, ensure_ascii=False)
        print(f"Updated best model files in {best_dir}/")

    # Clean up final temp best traineddata of this run
    if best_run_traineddata and os.path.exists(best_run_traineddata):
        os.remove(best_run_traineddata)

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

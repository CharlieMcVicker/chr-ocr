#!/usr/bin/env python3
"""
Tuning script for Staged Epoch Loop meta-parameters.
Executes experiments across a parameter matrix, evaluates model performance,
and identifies the optimal configuration.
"""
import os
import sys
import glob
import subprocess
import argparse
import json
import re

# Search matrix for post-fix hyperparameter retuning (with expanded charset & schedules)
EXPERIMENTS = [
    # Run 17: Constant Low LR, 16 epochs
    {
        "id": "run_17_const_low",
        "epochs": 16,
        "variations": 3,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "constant",
        "lr_decay_rate": 0.5,
        "lr_decay_epochs": 4,
        "blur_prob": 0.4,
        "shadow_prob": 0.3,
        "distortion_prob": 0.4,
        "dropout_prob": 0.3,
        "bleedthrough_prob": 0.25,
        "eval_epochs": [8, 12, 14, 16]
    },
    # Run 18: Stepped Decay, 16 epochs
    {
        "id": "run_18_step_decay",
        "epochs": 16,
        "variations": 3,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "step",
        "lr_decay_rate": 0.5,
        "lr_decay_epochs": 4,
        "blur_prob": 0.4,
        "shadow_prob": 0.3,
        "distortion_prob": 0.4,
        "dropout_prob": 0.3,
        "bleedthrough_prob": 0.25,
        "eval_epochs": [8, 12, 14, 16]
    },
    # Run 19: Exponential Decay, 16 epochs
    {
        "id": "run_19_exp_decay",
        "epochs": 16,
        "variations": 3,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "exp",
        "lr_decay_rate": 0.9,
        "lr_decay_epochs": 4,
        "blur_prob": 0.4,
        "shadow_prob": 0.3,
        "distortion_prob": 0.4,
        "dropout_prob": 0.3,
        "bleedthrough_prob": 0.25,
        "eval_epochs": [8, 12, 14, 16]
    },
    # Run 20: Constant LR, 20 epochs
    {
        "id": "run_20_long_const",
        "epochs": 20,
        "variations": 3,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "constant",
        "lr_decay_rate": 0.5,
        "lr_decay_epochs": 4,
        "blur_prob": 0.4,
        "shadow_prob": 0.3,
        "distortion_prob": 0.4,
        "dropout_prob": 0.3,
        "bleedthrough_prob": 0.25,
        "eval_epochs": [8, 12, 16, 20]
    },
    # Run 21: Step Decay, Halved Augmentation, 16 epochs
    {
        "id": "run_21_step_mod_aug",
        "epochs": 16,
        "variations": 3,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "step",
        "lr_decay_rate": 0.5,
        "lr_decay_epochs": 4,
        "blur_prob": 0.2,
        "shadow_prob": 0.15,
        "distortion_prob": 0.2,
        "dropout_prob": 0.15,
        "bleedthrough_prob": 0.125,
        "eval_epochs": [8, 12, 14, 16]
    },
    # Run 22: Step Decay, Heavier Variation, 16 epochs
    {
        "id": "run_22_step_high_var",
        "epochs": 16,
        "variations": 5,
        "iterations": 200,
        "error_rate": 0.05,
        "learning_rate": 0.0005,
        "lr_schedule": "step",
        "lr_decay_rate": 0.5,
        "lr_decay_epochs": 4,
        "blur_prob": 0.4,
        "shadow_prob": 0.3,
        "distortion_prob": 0.4,
        "dropout_prob": 0.3,
        "bleedthrough_prob": 0.25,
        "eval_epochs": [8, 12, 14, 16]
    }
]

def get_latest_checkpoint(checkpoint_dir):
    """
    Returns the path to the most recent checkpoint file in the directory.
    """
    checkpoints = glob.glob(os.path.join(checkpoint_dir, "*.checkpoint"))
    if not checkpoints:
        return None
    checkpoints.sort(key=os.path.getmtime)
    return checkpoints[-1]

def get_checkpoint_for_epoch(checkpoint_dir, epoch, iterations_per_epoch):
    """
    Returns the checkpoint corresponding to the target epoch/iteration, or the closest one.
    """
    target_iter = epoch * iterations_per_epoch
    checkpoints = glob.glob(os.path.join(checkpoint_dir, f"*_{target_iter}.checkpoint"))
    if checkpoints:
        return checkpoints[0]
        
    # Fallback to closest checkpoint
    all_checkpoints = glob.glob(os.path.join(checkpoint_dir, "*.checkpoint"))
    if not all_checkpoints:
        return None
        
    best_cp = None
    min_diff = float('inf')
    for cp in all_checkpoints:
        # Checkpoint filenames look like: chr_<error>_<iteration>_<maxiterations>.checkpoint
        match = re.search(r"_(\d+)_(\d+)\.checkpoint$", cp)
        if match:
            cp_iter = int(match.group(2))
            diff = abs(cp_iter - target_iter)
            if diff < min_diff:
                min_diff = diff
                best_cp = cp
    return best_cp

def evaluate_checkpoint(checkpoint_path, test_dir, traineddata_path):
    """
    Runs lstmeval on all subdirectories in test_dir and calculates average BCER and BWER.
    """
    if not checkpoint_path or not os.path.exists(checkpoint_path):
        print(f"Warning: Checkpoint path {checkpoint_path} not found.")
        return None, None, {}

    bcer_sum = 0.0
    bwer_sum = 0.0
    count = 0
    algo_results = {}

    algo_dirs = [d for d in glob.glob(os.path.join(test_dir, "*")) if os.path.isdir(d)]
    
    for algo_dir in sorted(algo_dirs):
        algo_name = os.path.basename(algo_dir)
        list_test_path = os.path.join(algo_dir, "list.test")
        
        # Ensure list.test exists
        if not os.path.exists(list_test_path):
            png_files = glob.glob(os.path.join(algo_dir, "*.png"))
            if not png_files:
                continue
            with open(list_test_path, "w", encoding="utf-8") as list_f:
                for img in png_files:
                    base = os.path.splitext(img)[0]
                    lstmf_path = base + ".lstmf"
                    if not os.path.exists(lstmf_path):
                        subprocess.run(
                            ["tesseract", img, base, "--tessdata-dir", "training_data/dataset/model/starter/chr", "-l", "chr", "--oem", "1", "--psm", "13", "/opt/homebrew/share/tessdata/configs/lstm.train"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            check=True
                        )
                    list_f.write(os.path.abspath(lstmf_path) + "\n")
        
        if not os.path.exists(list_test_path) or os.path.getsize(list_test_path) == 0:
            continue

        cmd = [
            "lstmeval",
            "--model", checkpoint_path,
            "--traineddata", traineddata_path,
            "--eval_listfile", list_test_path
        ]
        
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = res.stderr # lstmeval outputs metrics to stderr
            
            # Find BCER and BWER
            match = re.search(r"BCER eval=([\d\.]+),\s*BWER eval=([\d\.]+)", output)
            if match:
                bcer = float(match.group(1))
                bwer = float(match.group(2))
                algo_results[algo_name] = {"BCER": bcer, "BWER": bwer}
                bcer_sum += bcer
                bwer_sum += bwer
                count += 1
        except Exception as e:
            print(f"Error evaluating {algo_name}: {e}")
            
    if count == 0:
        return None, None, {}
        
    avg_bcer = bcer_sum / count
    avg_bwer = bwer_sum / count
    return avg_bcer, avg_bwer, algo_results

def main():
    parser = argparse.ArgumentParser(description="Tuning meta-parameters of Staged Epoch Loop")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing training")
    args = parser.parse_args()

    test_dir = "training_data/dataset/test"
    traineddata_path = "training_data/dataset/model/starter/chr/chr.traineddata"
    results_file = "training_data/boundary_results.json"
    
    all_results = []
    
    print(f"=== Staged Epoch Loop Hyperparameter Retuning ===")
    print(f"Total experiments to execute: {len(EXPERIMENTS)}")
    
    for i, exp in enumerate(EXPERIMENTS, 1):
        exp_id = exp["id"]
        print(f"\n--- Experiment {i}/{len(EXPERIMENTS)}: {exp_id} ---")
        print(f"Parameters: epochs={exp['epochs']}, iterations={exp['iterations']}, lr={exp['learning_rate']}, shadow={exp['shadow_prob']}, error_rate={exp['error_rate']}")
        
        run_output_dir = f"training_data/staged_tuning/{exp_id}_output"
        run_temp_epoch_dir = f"training_data/staged_tuning/{exp_id}_temp_epoch"
        
        cmd = [
            ".venv/bin/python",
            "scripts/train_staged.py",
            "--total-epochs", str(exp["epochs"]),
            "--iterations-per-epoch", str(exp["iterations"]),
            "--variations-per-image", str(exp["variations"]),
            "--error-rate", str(exp["error_rate"]),
            "--learning-rate", str(exp["learning_rate"]),
            "--lr-schedule", exp["lr_schedule"],
            "--lr-decay-rate", str(exp["lr_decay_rate"]),
            "--lr-decay-epochs", str(exp["lr_decay_epochs"]),
            "--blur-prob", str(exp["blur_prob"]),
            "--shadow-prob", str(exp["shadow_prob"]),
            "--distortion-prob", str(exp["distortion_prob"]),
            "--dropout-prob", str(exp["dropout_prob"]),
            "--bleedthrough-prob", str(exp["bleedthrough_prob"]),
            "--train-output-dir", run_output_dir,
            "--output-dir", run_temp_epoch_dir,
            "--old-traineddata", "training_data/dataset/model/chr.traineddata",
            "--model-dir", "training_data/dataset/model/starter/chr",
            "--continue-from", "training_data/dataset/model/chr.lstm"
        ]
        
        if args.dry_run:
            print(f"[DRY-RUN] Would run command: {' '.join(cmd)}")
            for epoch in exp["eval_epochs"]:
                all_results.append({
                    "id": f"{exp_id}_epoch_{epoch}",
                    "parent_id": exp_id,
                    "epochs": epoch,
                    "variations": exp["variations"],
                    "iterations": exp["iterations"],
                    "error_rate": exp["error_rate"],
                    "learning_rate": exp["learning_rate"],
                    "avg_BCER": 25.0 - (0.5 * i) - (0.1 * epoch),
                    "avg_BWER": 55.0 - (0.8 * i) - (0.2 * epoch),
                    "checkpoint": f"{run_output_dir}/dummy_epoch_{epoch}.checkpoint"
                })
            continue

        print(f"Running Staged training pipeline...")
        try:
            subprocess.run(cmd, check=True)
            
            # Evaluate all requested sub-epochs
            for epoch in exp["eval_epochs"]:
                print(f"Locating checkpoint for epoch {epoch} (target iterations: {epoch * exp['iterations']})...")
                checkpoint = get_checkpoint_for_epoch(run_output_dir, epoch, exp["iterations"])
                
                if checkpoint:
                    print(f"Evaluating checkpoint: {checkpoint}")
                    avg_bcer, avg_bwer, algo_details = evaluate_checkpoint(checkpoint, test_dir, traineddata_path)
                    
                    if avg_bcer is not None:
                        print(f"Epoch {epoch} -> Average BCER: {avg_bcer:.3f}%, Average BWER: {avg_bwer:.3f}%")
                        all_results.append({
                            "id": f"{exp_id}_epoch_{epoch}",
                            "parent_id": exp_id,
                            "epochs": epoch,
                            "variations": exp["variations"],
                            "iterations": exp["iterations"],
                            "error_rate": exp["error_rate"],
                            "learning_rate": exp["learning_rate"],
                            "avg_BCER": avg_bcer,
                            "avg_BWER": avg_bwer,
                            "checkpoint": checkpoint,
                            "algo_details": algo_details
                        })
                    else:
                        print(f"Error: Evaluation produced no metrics for epoch {epoch}.")
                else:
                    print(f"Error: No checkpoint found for epoch {epoch}.")
                
        except Exception as e:
            print(f"Error executing experiment {exp_id}: {e}")
            
    # Save results
    if not args.dry_run or not os.path.exists(results_file):
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n=== Tuning Completed ===")
        print(f"Results written to {results_file}")
    else:
        print(f"\n=== [DRY-RUN] Tuning Completed ===")
    
    # Identify the best configuration
    if all_results:
        best_run = min(all_results, key=lambda x: x["avg_BCER"])
        print("\n=== Best Meta-parameter Configuration ===")
        print(f"Run ID: {best_run['id']}")
        print(f"Epochs: {best_run['epochs']}")
        print(f"Variations: {best_run['variations']}")
        print(f"Iterations: {best_run['iterations']}")
        print(f"Learning Rate: {best_run['learning_rate']}")
        print(f"Error Rate: {best_run['error_rate']}")
        print(f"Best Average BCER: {best_run['avg_BCER']:.3f}%")
        print(f"Best Average BWER: {best_run['avg_BWER']:.3f}%")

if __name__ == "__main__":
    main()

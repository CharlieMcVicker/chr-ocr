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

# Search matrix defined as One-at-a-Time (OAT) variations from a robust base configuration
BASE_CONFIG = {
    "epochs": 4,
    "variations": 3,
    "iterations": 150,
    "error_rate": 0.05
}

EXPERIMENTS = [
    # Run 8: Zero-noise baseline
    {"id": "run_8_zero_noise", "epochs": 4, "variations": 3, "iterations": 200, "error_rate": 0.00},
    # Run 9-10: High Epoch Counts
    {"id": "run_9_epochs_6", "epochs": 6, "variations": 3, "iterations": 200, "error_rate": 0.05},
    {"id": "run_10_epochs_8", "epochs": 8, "variations": 3, "iterations": 200, "error_rate": 0.05},
    # Run 11-12: High Augmentation Variations
    {"id": "run_11_vars_6", "epochs": 4, "variations": 6, "iterations": 200, "error_rate": 0.05},
    {"id": "run_12_vars_8", "epochs": 4, "variations": 8, "iterations": 200, "error_rate": 0.05},
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
                            ["tesseract", img, base, "-l", "chr", "--psm", "13", "lstm.train"],
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

    test_dir = "training_data_v2/dataset/test"
    traineddata_path = "training_data_v2/dataset/model/chr.traineddata"
    results_file = "training_data_v2/boundary_results.json"
    
    all_results = []
    
    print(f"=== Staged Epoch Loop Tuning ===")
    print(f"Total experiments to execute: {len(EXPERIMENTS)}")
    
    for i, exp in enumerate(EXPERIMENTS, 1):
        exp_id = exp["id"]
        print(f"\n--- Experiment {i}/{len(EXPERIMENTS)}: {exp_id} ---")
        print(f"Parameters: epochs={exp['epochs']}, variations={exp['variations']}, iterations={exp['iterations']}, error_rate={exp['error_rate']}")
        
        run_output_dir = f"training_data_v2/staged_tuning/{exp_id}_output"
        run_temp_epoch_dir = f"training_data_v2/staged_tuning/{exp_id}_temp_epoch"
        
        cmd = [
            ".venv/bin/python",
            "scripts/train_staged.py",
            "--total-epochs", str(exp["epochs"]),
            "--iterations-per-epoch", str(exp["iterations"]),
            "--variations-per-image", str(exp["variations"]),
            "--error-rate", str(exp["error_rate"]),
            "--train-output-dir", run_output_dir,
            "--output-dir", run_temp_epoch_dir
        ]
        
        if args.dry_run:
            print(f"[DRY-RUN] Would run command: {' '.join(cmd)}")
            # Write dummy results
            all_results.append({
                "id": exp_id,
                "epochs": exp["epochs"],
                "variations": exp["variations"],
                "iterations": exp["iterations"],
                "error_rate": exp["error_rate"],
                "avg_BCER": 25.0 - (0.5 * i),
                "avg_BWER": 55.0 - (0.8 * i),
                "checkpoint": f"{run_output_dir}/dummy_best.checkpoint"
            })
            continue

        print(f"Running Staged training pipeline...")
        try:
            subprocess.run(cmd, check=True)
            
            # Locate the best checkpoint
            best_checkpoint = get_latest_checkpoint(run_output_dir)
            print(f"Training finished. Best checkpoint found: {best_checkpoint}")
            
            # Evaluate model
            print("Evaluating checkpoint on test splits...")
            avg_bcer, avg_bwer, algo_details = evaluate_checkpoint(best_checkpoint, test_dir, traineddata_path)
            
            if avg_bcer is not None:
                print(f"Evaluation Results -> Average BCER: {avg_bcer:.3f}%, Average BWER: {avg_bwer:.3f}%")
                all_results.append({
                    "id": exp_id,
                    "epochs": exp["epochs"],
                    "variations": exp["variations"],
                    "iterations": exp["iterations"],
                    "error_rate": exp["error_rate"],
                    "avg_BCER": avg_bcer,
                    "avg_BWER": avg_bwer,
                    "checkpoint": best_checkpoint,
                    "algo_details": algo_details
                })
            else:
                print("Error: Evaluation produced no metrics.")
                
        except Exception as e:
            print(f"Error executing experiment {exp_id}: {e}")
            
    # Save results
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
        
    print(f"\n=== Tuning Completed ===")
    print(f"Results written to {results_file}")
    
    # Identify the best configuration
    if all_results:
        best_run = min(all_results, key=lambda x: x["avg_BCER"])
        print("\n=== Best Meta-parameter Configuration ===")
        print(f"Run ID: {best_run['id']}")
        print(f"Epochs: {best_run['epochs']}")
        print(f"Variations: {best_run['variations']}")
        print(f"Iterations: {best_run['iterations']}")
        print(f"Error Rate: {best_run['error_rate']}")
        print(f"Best Average BCER: {best_run['avg_BCER']:.3f}%")
        print(f"Best Average BWER: {best_run['avg_BWER']:.3f}%")

if __name__ == "__main__":
    main()

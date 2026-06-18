#!/usr/bin/env python3
"""
Task-98 Hyperparameter Sweep Runner for Phoenix/CNT Mixture Ratios.
Runs staged training runs for 90/10, 80/20, and 70/30 mixture ratios,
and evaluates model performance on Phoenix and CNT test splits.
"""
import os
import sys
import argparse
import subprocess
import json
import re
import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.config import SweepConfig, TrainingConfig
from phoenix.training.sweep import get_checkpoint_for_epoch, evaluate_checkpoint

def main():
    parser = argparse.ArgumentParser(description="Sweep and tune Phoenix/CNT mixture ratios")
    parser.add_argument("--sweep-config", default="configs/sweep_mixture_ratio.json")
    parser.add_argument("--dataset-dir", default="training_data/dataset")
    parser.add_argument("--results-file", default="training_data/sweep_mixture_results.json")
    args = parser.parse_args()

    if not os.path.exists(args.sweep_config):
        print(f"Error: Sweep config file not found at {args.sweep_config}")
        sys.exit(1)

    sweep_config = SweepConfig.load_from_json(args.sweep_config)
    experiments = sweep_config.experiments
    all_results = []

    test_dir = args.dataset_dir
    traineddata_path = "training_data/dataset/model/starter/chr/chr.traineddata"

    print(f"=== Starting Mixture Ratio Sweep ({len(experiments)} experiments) ===")
    for i, exp in enumerate(experiments, 1):
        exp_id = exp.id
        exp_config = exp.config
        
        print(f"\n--- Experiment {i}/{len(experiments)}: {exp_id} ---")
        print(f"Mixture ratio: {exp_config.mixture_ratio}")
        
        run_output_dir = f"training_data/staged_tuning/{exp_id}_output"
        run_temp_epoch_dir = f"training_data/staged_tuning/{exp_id}_temp_epoch"
        
        # Override directories/paths for isolated run
        exp_config.train_output_dir = run_output_dir
        exp_config.output_dir = run_temp_epoch_dir
        exp_config.continue_from = "training_data/dataset/model/chr.lstm"
        exp_config.model_dir = "training_data/dataset/model/starter/chr"
        exp_config.old_traineddata = "training_data/dataset/model/chr.traineddata"
        
        os.makedirs(run_output_dir, exist_ok=True)
        config_path = os.path.join(run_output_dir, "config.json")
        exp_config.save_to_json(config_path)
        
        cmd = [
            sys.executable,
            "scripts/train_staged.py",
            "--config", config_path
        ]
        
        print(f"Executing staged training loop for {exp_id}...")
        subprocess.run(cmd, check=True)
        
        # Evaluate each sub-epoch checkpoint on Phoenix and CNT splits
        for epoch in exp.eval_epochs:
            print(f"Locating checkpoint for epoch {epoch}...")
            checkpoint = get_checkpoint_for_epoch(run_output_dir, epoch, exp_config.iterations_per_epoch)
            
            if checkpoint and os.path.exists(checkpoint):
                print(f"Evaluating checkpoint: {checkpoint}")
                # We want to extract .traineddata from checkpoint to run evaluate_mixed_model.py
                temp_traineddata = f"{run_output_dir}/chr_eval_temp.traineddata"
                if os.path.exists(temp_traineddata):
                    os.remove(temp_traineddata)
                
                unpack_cmd = [
                    "lstmtraining",
                    "--stop_training",
                    "--continue_from", checkpoint,
                    "--traineddata", traineddata_path,
                    "--model_output", temp_traineddata
                ]
                subprocess.run(unpack_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                
                # Now evaluate the temporary model using evaluate_mixed_model.py
                eval_cmd = [
                    sys.executable,
                    "scripts/evaluate_mixed_model.py",
                    "--model-dir", run_output_dir,
                    "--lang", "chr_eval_temp",
                    "--dataset-dir", test_dir
                ]
                res = subprocess.run(eval_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
                
                # Parse output to find Phoenix and CNT metrics
                eval_stdout = res.stdout
                print(eval_stdout)
                
                phx_cer = None
                phx_wer = None
                cnt_cer = None
                cnt_wer = None
                weighted_cer = None
                weighted_wer = None
                
                # Parse lines using regex
                # Example: Phoenix Test Set (101 lines):
                #            Mean CER: 6.75%
                #            Mean WER: 22.61%
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
                
                if phx_cer is not None and cnt_cer is not None:
                    all_results.append({
                        "id": f"{exp_id}_epoch_{epoch}",
                        "parent_id": exp_id,
                        "epochs": epoch,
                        "mixture_ratio": exp_config.mixture_ratio,
                        "phoenix_CER": phx_cer,
                        "phoenix_WER": phx_wer,
                        "cnt_CER": cnt_cer,
                        "cnt_WER": cnt_wer,
                        "weighted_CER": weighted_cer,
                        "weighted_WER": weighted_wer,
                        "checkpoint": checkpoint
                    })
                
                if os.path.exists(temp_traineddata):
                    os.remove(temp_traineddata)
            else:
                print(f"Warning: Checkpoint not found for epoch {epoch}")

    # Save all results to json
    with open(args.results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nAll results saved to {args.results_file}")

    if all_results:
        # Sort and identify best config (lowest weighted CER)
        best_run = min(all_results, key=lambda x: x["weighted_CER"])
        print("\n=== Best Mixture Ratio Sweep Run ===")
        print(f"Run ID: {best_run['id']}")
        print(f"Mixture ratio: {best_run['mixture_ratio']}")
        print(f"Epoch: {best_run['epochs']}")
        print(f"Phoenix CER: {best_run['phoenix_CER']}%")
        print(f"CNT CER: {best_run['cnt_CER']}%")
        print(f"Weighted CER: {best_run['weighted_CER']}%")
        
        # Save best config as configs/train_mixed.json
        best_exp = next(e for e in experiments if e.id == best_run['parent_id'])
        best_exp.config.save_to_json("configs/train_mixed.json")
        print("Updated configs/train_mixed.json with the optimal sweep parameters.")

if __name__ == "__main__":
    main()

"""
Tuning module for Staged Epoch Loop meta-parameters.
Executes experiments across a parameter matrix, evaluates model performance,
and identifies the optimal configuration.
"""

import os
import sys
import glob
import subprocess
import json
import re

from typing import Optional
from phoenix.config import SweepConfig, TrainingConfig
from phoenix.training.eval import compile_checkpoint, evaluate_checkpoint as evaluate_checkpoint_mixed


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

def run_meta_parameter_sweep(
    sweep_config: SweepConfig,
    test_dir: str,
    traineddata_path: str,
    results_file: str,
    dry_run: bool = False,
    sweep_name: Optional[str] = None,
    best_config_path: str = "best_config.json"
):
    """
    Executes a sweep of experiments across a parameter matrix, evaluations, and saves results.
    """
    experiments = sweep_config.experiments
    all_results = []
    
    print(f"=== Staged Epoch Loop Hyperparameter Retuning ===")
    print(f"Total experiments to execute: {len(experiments)}")
    
    # Derive master pool prefix and clean up old pools before starting
    master_pool_prefix = None
    if sweep_name:
        master_pool_prefix = f"master_pool_{sweep_name}"
        import shutil
        print(f"Cleaning up existing master pool directories for prefix '{master_pool_prefix}'...")
        for epoch in range(1, 100):
            pool_dir = f"training_data/staged_tuning/{master_pool_prefix}_epoch_{epoch}"
            if os.path.exists(pool_dir):
                print(f"Removing old master pool: {pool_dir}")
                shutil.rmtree(pool_dir)
    
    for i, exp in enumerate(experiments, 1):
        exp_id = exp.id
        exp_config = exp.config
        
        print(f"\n--- Experiment {i}/{len(experiments)}: {exp_id} ---")
        print(f"Mixture ratio: {exp_config.mixture_ratio}")
        
        run_output_dir = f"training_data/staged_tuning/{exp_id}_output"
        run_temp_epoch_dir = f"training_data/staged_tuning/{exp_id}_temp_epoch"
        
        # Override paths to run in isolation
        exp_config.train_output_dir = run_output_dir
        exp_config.output_dir = run_temp_epoch_dir
        if not exp_config.continue_from:
            exp_config.continue_from = "training_data/dataset/model/chr.lstm"
        if not exp_config.model_dir:
            exp_config.model_dir = "training_data/dataset/model"
        if not exp_config.old_traineddata:
            exp_config.old_traineddata = "training_data/dataset/model/chr.traineddata"
        if master_pool_prefix:
            exp_config.master_pool_prefix = master_pool_prefix
            
        os.makedirs(run_output_dir, exist_ok=True)
        config_path = os.path.join(run_output_dir, "config.json")
        exp_config.save_to_json(config_path)
        
        cmd = [
            sys.executable,
            "scripts/train_staged.py",
            "--config", config_path
        ]
        
        if dry_run:
            print(f"[DRY-RUN] Would run command: {' '.join(cmd)}")
            for epoch in exp.eval_epochs:
                all_results.append({
                    "id": f"{exp_id}_epoch_{epoch}",
                    "parent_id": exp_id,
                    "epochs": epoch,
                    "mixture_ratio": exp_config.mixture_ratio,
                    "phoenix_CER": 10.0 - (0.2 * i) - (0.05 * epoch),
                    "phoenix_WER": 30.0 - (0.5 * i) - (0.1 * epoch),
                    "cnt_CER": 15.0 - (0.3 * i) - (0.07 * epoch),
                    "cnt_WER": 40.0 - (0.8 * i) - (0.2 * epoch),
                    "weighted_CER": 12.0 - (0.25 * i) - (0.06 * epoch),
                    "weighted_WER": 35.0 - (0.6 * i) - (0.15 * epoch),
                    "checkpoint": f"{run_output_dir}/dummy_epoch_{epoch}.checkpoint"
                })
            continue
            
        print(f"Running Staged training pipeline...")
        try:
            subprocess.run(cmd, check=True)
            
            # Evaluate all requested sub-epochs
            for epoch in exp.eval_epochs:
                print(f"Locating checkpoint for epoch {epoch} (target iterations: {epoch * exp_config.iterations_per_epoch})...")
                checkpoint = get_checkpoint_for_epoch(run_output_dir, epoch, exp_config.iterations_per_epoch)
                
                if checkpoint:
                    print(f"Evaluating checkpoint: {checkpoint}")
                    # Print a clear, prominent header identifying the epoch/checkpoint being evaluated
                    print(f"\n==================================================")
                    print(f" EVALUATING CHECKPOINT FOR EPOCH {epoch}")
                    print(f" Checkpoint: {os.path.basename(checkpoint)}")
                    print(f"==================================================")
                    
                    temp_traineddata = os.path.join(run_output_dir, "chr_eval_temp.traineddata")
                    if compile_checkpoint(checkpoint, traineddata_path, temp_traineddata):
                        metrics = evaluate_checkpoint_mixed(
                            checkpoint_path=checkpoint,
                            traineddata_path=temp_traineddata,
                            train_output_dir=run_output_dir,
                            lang="chr_eval_temp"
                        )
                        if metrics:
                            res_item = {
                                "id": f"{exp_id}_epoch_{epoch}",
                                "parent_id": exp_id,
                                "epochs": epoch,
                                "mixture_ratio": exp_config.mixture_ratio,
                                "phoenix_CER": metrics.get("phoenix_CER"),
                                "phoenix_WER": metrics.get("phoenix_WER"),
                                "cnt_CER": metrics.get("cnt_CER"),
                                "cnt_WER": metrics.get("cnt_WER"),
                                "weighted_CER": metrics.get("weighted_CER"),
                                "weighted_WER": metrics.get("weighted_WER"),
                                "checkpoint": checkpoint
                            }
                            all_results.append(res_item)
                            print(f"Epoch {epoch} -> Phoenix CER: {metrics.get('phoenix_CER') or 0.0:.2f}%, CNT CER: {metrics.get('cnt_CER') or 0.0:.2f}%, Weighted CER: {metrics.get('weighted_CER') or 0.0:.2f}%")
                        else:
                            print(f"Error: Evaluation produced no metrics for epoch {epoch}.")
                        
                        if os.path.exists(temp_traineddata):
                            os.remove(temp_traineddata)
                    else:
                        print(f"Error: Failed to compile checkpoint for epoch {epoch}.")
                else:
                    print(f"Error: No checkpoint found for epoch {epoch}.")
                    
        except Exception as e:
            print(f"Error executing experiment {exp_id}: {e}")
            
    # Save results
    if not dry_run or not os.path.exists(results_file):
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"\n=== Tuning Completed ===")
        print(f"Results written to {results_file}")
    else:
        print(f"\n=== [DRY-RUN] Tuning Completed ===")
        
    # Identify the best configuration
    if all_results:
        best_run = min(all_results, key=lambda x: x["weighted_CER"])
        print("\n=== Best Mixture Ratio Sweep Run ===")
        print(f"Run ID: {best_run['id']}")
        print(f"Mixture ratio: {best_run['mixture_ratio']}")
        print(f"Epoch: {best_run['epochs']}")
        print(f"Phoenix CER: {best_run['phoenix_CER']}%")
        print(f"CNT CER: {best_run['cnt_CER']}%")
        print(f"Weighted CER: {best_run['weighted_CER']}%")
            
        # Save best config
        best_exp = next((e for e in experiments if e.id == best_run['parent_id']), None)
        if best_exp:
            best_config = best_exp.config
            best_config.total_epochs = best_run['epochs']
            
            # Make sure target dir for best config exists
            os.makedirs(os.path.dirname(os.path.abspath(best_config_path)), exist_ok=True)
            best_config.save_to_json(best_config_path)
            print(f"Saved best configuration to {best_config_path}")



class SweepSampler:
    """
    Reads the metadata index generated by augment_dynamic.py and filters/samples
    .lstmf files to construct unique train.list files matching each experiment's
    target probabilities.
    """
    @staticmethod
    def sample_to_list(metadata_index_path: str, output_list_path: str, mixture_ratio: float, epoch: int, max_cnt_samples: Optional[int] = None):
        import json
        import random
        import os
        from typing import Optional

        if not os.path.exists(metadata_index_path):
            raise FileNotFoundError(f"Metadata index not found at: {metadata_index_path}")

        with open(metadata_index_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        # Separate records by dataset and group by original sample ID
        phoenix_records = {}
        cnt_records = {}

        for r in records:
            item_id = r["id"]
            dataset = r.get("dataset", "phoenix")
            if dataset == "cnt":
                if item_id not in cnt_records:
                    cnt_records[item_id] = []
                cnt_records[item_id].append(r)
            else:
                if item_id not in phoenix_records:
                    phoenix_records[item_id] = []
                phoenix_records[item_id].append(r)

        phoenix_unique_ids = sorted(phoenix_records.keys())
        cnt_unique_ids = sorted(cnt_records.keys())

        n_phoenix = len(phoenix_unique_ids)
        
        # Calculate target CNT unique samples
        if mixture_ratio >= 1.0:
            n_cnt = 0
        elif mixture_ratio <= 0.0:
            n_cnt = len(cnt_unique_ids)
        else:
            if n_phoenix == 0:
                n_cnt = int(len(cnt_unique_ids) * (1.0 - mixture_ratio))
                if n_cnt == 0 and cnt_unique_ids:
                    n_cnt = 1
            else:
                n_cnt = int(n_phoenix * (1.0 - mixture_ratio) / mixture_ratio)

        # Cap by max_cnt_samples if specified
        if max_cnt_samples is not None:
            n_cnt = min(n_cnt, max_cnt_samples)

        # Seeded stable sampling of CNT lines

        seed_str = f"cnt_batch_salt_epoch_{epoch}"
        rng = random.Random(seed_str)

        sampled_cnt_ids = []
        if n_cnt > 0 and cnt_unique_ids:
            # Separate CNT by rare status (check has_rare of any of its variations)
            rare_cnt_ids = []
            common_cnt_ids = []
            for item_id in cnt_unique_ids:
                has_rare = any(v.get("has_rare", False) for v in cnt_records[item_id])
                if has_rare:
                    rare_cnt_ids.append(item_id)
                else:
                    common_cnt_ids.append(item_id)

            rng.shuffle(rare_cnt_ids)
            rng.shuffle(common_cnt_ids)

            sampled_count = min(n_cnt, len(cnt_unique_ids))
            if len(rare_cnt_ids) >= sampled_count:
                sampled_cnt_ids = rare_cnt_ids[:sampled_count]
            else:
                needed = sampled_count - len(rare_cnt_ids)
                sampled_cnt_ids = rare_cnt_ids + common_cnt_ids[:needed]

        # Gather all .lstmf paths
        selected_lstmf_paths = []
        
        # All phoenix variations
        for item_id in phoenix_unique_ids:
            for r in phoenix_records[item_id]:
                if r.get("lstmf_path"):
                    selected_lstmf_paths.append(r["lstmf_path"])

        # Sampled CNT variations
        for item_id in sampled_cnt_ids:
            for r in cnt_records[item_id]:
                if r.get("lstmf_path"):
                    selected_lstmf_paths.append(r["lstmf_path"])

        # Write to target train.list file
        os.makedirs(os.path.dirname(os.path.abspath(output_list_path)), exist_ok=True)
        with open(output_list_path, "w", encoding="utf-8") as out_f:
            for path in selected_lstmf_paths:
                out_f.write(path + "\n")

        print(f"SweepSampler: Sampled {len(phoenix_unique_ids)} Phoenix unique lines and {len(sampled_cnt_ids)} CNT unique lines.")
        print(f"SweepSampler: Wrote {len(selected_lstmf_paths)} .lstmf paths to {output_list_path} (Target Mixture Ratio: {mixture_ratio:.4f})")
        return len(selected_lstmf_paths)

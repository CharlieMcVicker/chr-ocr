#!/usr/bin/env python3
"""
Tuning script for Staged Epoch Loop meta-parameters.
Executes experiments across a parameter matrix, evaluates model performance,
and identifies the optimal configuration.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.config import SweepConfig
from phoenix.training.sweep import run_meta_parameter_sweep

def main():
    parser = argparse.ArgumentParser(description="Tuning meta-parameters of Staged Epoch Loop")
    parser.add_argument("--sweep-config", default="scripts/sweep_config.json", help="Path to JSON configuration for the sweep")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing training")
    parser.add_argument("--dataset-dir", default=None, help="Root dataset or test directory path")
    parser.add_argument("--results-file", default=None, help="Path to save sweep results JSON file")
    parser.add_argument("--traineddata-path", default=None, help="Path to baseline .traineddata file")
    parser.add_argument("--best-config-path", default=None, help="Path to save the best configuration json")
    args = parser.parse_args()

    if not os.path.exists(args.sweep_config):
        print(f"Error: Sweep config file not found at {args.sweep_config}")
        sys.exit(1)

    sweep_name = os.path.splitext(os.path.basename(args.sweep_config))[0]

    # Set up defaults for mixed evaluation
    dataset_dir = args.dataset_dir if args.dataset_dir else "training_data/dataset"
    traineddata_path = args.traineddata_path if args.traineddata_path else "training_data/dataset/model/chr.traineddata"
    results_file = args.results_file if args.results_file else f"training_data/{sweep_name}_results.json"
    best_config_path = args.best_config_path if args.best_config_path else "configs/train_mixed.json"
        
    sweep_config = SweepConfig.load_from_json(args.sweep_config)
    run_meta_parameter_sweep(
        sweep_config=sweep_config,
        test_dir=dataset_dir,
        traineddata_path=traineddata_path,
        results_file=results_file,
        dry_run=args.dry_run,
        sweep_name=sweep_name,
        best_config_path=best_config_path
    )

if __name__ == "__main__":
    main()



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
    args = parser.parse_args()

    test_dir = "training_data/dataset/test"
    traineddata_path = "training_data/dataset/model/starter/chr/chr.traineddata"
    results_file = "training_data/boundary_results.json"
    
    if not os.path.exists(args.sweep_config):
        print(f"Error: Sweep config file not found at {args.sweep_config}")
        sys.exit(1)
        
    sweep_config = SweepConfig.load_from_json(args.sweep_config)
    run_meta_parameter_sweep(
        sweep_config=sweep_config,
        test_dir=test_dir,
        traineddata_path=traineddata_path,
        results_file=results_file,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    main()

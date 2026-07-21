#!/usr/bin/env python3
"""
CLI utility to evaluate a custom slice of Tesseract training checkpoints.
"""
import os
import sys
import argparse
import tempfile
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from phoenix.training.eval import (
    get_sorted_checkpoints,
    compile_checkpoint,
    evaluate_checkpoint
)

def main():
    parser = argparse.ArgumentParser(description="Evaluate custom checkpoint slices on Phoenix and CNT test sets.")
    parser.add_argument("--model-dir", required=True, help="Directory containing Tesseract .checkpoint files")
    parser.add_argument("--traineddata", default="dataset/model/chr.traineddata", help="Base traineddata for stop_training compilation")
    parser.add_argument("--slice", default="[-5:]", help="Python-style slice string (e.g. '[-10:-5]', '[-5:]')")
    args = parser.parse_args()

    if not os.path.exists(args.model_dir):
        print(f"Error: Model directory '{args.model_dir}' does not exist.")
        sys.exit(1)
        
    if not os.path.exists(args.traineddata):
        print(f"Error: Base traineddata file '{args.traineddata}' does not exist.")
        sys.exit(1)

    checkpoints = get_sorted_checkpoints(args.model_dir, args.slice)
    if not checkpoints:
        print(f"No checkpoints matching slice '{args.slice}' found in '{args.model_dir}'.")
        sys.exit(0)

    print(f"\nFound {len(checkpoints)} checkpoints matching slice '{args.slice}'. Compiling and evaluating...")

    results = []
    for idx, cp in enumerate(checkpoints, 1):
        print(f"\n[{idx}/{len(checkpoints)}] Processing: {os.path.basename(cp)}")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_traineddata = os.path.join(tmpdir, "chr.traineddata")
            
            # Compile .checkpoint to .traineddata
            if not compile_checkpoint(cp, args.traineddata, temp_traineddata):
                continue
                
            # Evaluate using phoenix/training/evaluate_mixed_model.py
            metrics = evaluate_checkpoint(cp, args.traineddata, tmpdir, "chr")
            if metrics:
                results.append(metrics)
                print(f"  Phoenix CER:  {metrics['phoenix_CER']}%  (WER: {metrics['phoenix_WER']}%)")
                print(f"  CNT CER:      {metrics['cnt_CER']}%  (WER: {metrics['cnt_WER']}%)")
                print(f"  Weighted CER: {metrics['weighted_CER']}%  (WER: {metrics['weighted_WER']}%)")

    # Display results table
    if results:
        print("\n" + "="*80)
        print(f"{'Checkpoint':<30} | {'Phoenix CER (%)':<15} | {'CNT CER (%)':<12} | {'Weighted CER (%)':<15}")
        print("-"*80)
        for r in results:
            cp_name = os.path.basename(r["checkpoint_path"])
            # truncate name if too long for layout
            if len(cp_name) > 30:
                cp_name = cp_name[:27] + "..."
            print(f"{cp_name:<30} | {r['phoenix_CER']:<15} | {r['cnt_CER']:<12} | {r['weighted_CER']:<15}")
        print("="*80 + "\n")
    else:
        print("\nNo checkpoints were successfully compiled and evaluated.")

if __name__ == "__main__":
    main()

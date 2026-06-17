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
from phoenix.training.train import run_staged_training

def main():
    parser = argparse.ArgumentParser(description="Staged Epoch Loop for Tesseract OCR Fine-tuning")
    parser.add_argument("--config", default=None, help="Path to JSON configuration file (overrides other command line options)")
    parser.add_argument("--total-epochs", type=int, default=12, help="Total number of staged training epochs")
    parser.add_argument("--iterations-per-epoch", type=int, default=200, help="Number of training iterations to run per epoch")
    parser.add_argument("--train-manifest", default="training_data/manifest_w_lang.json", help="Path to raw master manifest")
    parser.add_argument("--variations-per-image", type=int, default=3, help="Fresh variations to generate per source image each epoch")
    parser.add_argument("--error-rate", type=float, default=0.05, help="Weakly supervised synthetic transcription error rate")
    parser.add_argument("--output-dir", default="training_data/dataset_epoch", help="Temporary directory for epoch dynamic dataset")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Directory containing base models")
    parser.add_argument("--train-output-dir", default="training_data/dataset_staged_output", help="Directory where checkpoints and logs are saved")
    parser.add_argument("--continue-from", default=None, help="Explicit checkpoint path to start training from")
    parser.add_argument("--old-traineddata", default=None, help="Path to the original traineddata (required for network expansion)")
    parser.add_argument("--max-workers", type=int, default=None, help="Maximum number of worker threads for parallel compilation")
    parser.add_argument("--use-dynamic-cnt", action="store_true", help="Enable dynamic epoch-by-epoch selection of CNT samples")
    parser.add_argument("--cnt-fraction", type=float, default=0.1, help="Fraction of CNT lines to sample per epoch")
    parser.add_argument("--cnt-dir", default="training_data/cnt", help="Directory containing CNT books")
    parser.add_argument("--learning-rate", type=float, default=0.0005, help="Learning rate for lstmtraining")
    parser.add_argument("--lr-schedule", default="constant", choices=["constant", "step", "exp"], help="Learning rate schedule type")
    parser.add_argument("--lr-decay-rate", type=float, default=0.5, help="Decay factor for learning rate schedule")
    parser.add_argument("--lr-decay-epochs", type=int, default=4, help="Epoch interval for step decay")
    parser.add_argument("--blur-prob", type=float, default=0.4, help="Probability of blur augmentation")
    parser.add_argument("--shadow-prob", type=float, default=0.3, help="Probability of shadow augmentation")
    parser.add_argument("--distortion-prob", type=float, default=0.4, help="Probability of distortion augmentation")
    parser.add_argument("--dropout-prob", type=float, default=0.3, help="Probability of dropout augmentation")
    parser.add_argument("--bleedthrough-prob", type=float, default=0.25, help="Probability of bleedthrough augmentation")
    args = parser.parse_args()

    # Load configuration
    if args.config:
        print(f"Loading configuration from JSON: {args.config}")
        config = TrainingConfig.load_from_json(args.config)
    else:
        # Build config from command line arguments
        config_data = vars(args)
        # remove config field itself
        config_data.pop("config", None)
        config = TrainingConfig.from_dict(config_data)

    run_staged_training(config)

if __name__ == "__main__":
    main()

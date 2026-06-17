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
    parser = argparse.ArgumentParser(description="Staged Epoch Loop for Tesseract OCR Fine-tuning (JSON Config Enforced)")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file (strictly required)")
    args = parser.parse_args()

    print(f"Loading configuration from JSON: {args.config}")
    config = TrainingConfig.load_from_json(args.config)

    run_staged_training(config)

if __name__ == "__main__":
    main()

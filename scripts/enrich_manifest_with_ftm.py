#!/usr/bin/env python3
"""
This module enriches the existing `manifest_w_lang.json` manifest with OCR transcriptions
and word-level confidence scores produced by the best fine-tuned Cherokee Tesseract LSTM model.
It gathers performance statistics to identify low-confidence predictions for targeted review.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.layout import enrich_manifest_with_ftm


def main():
    parser = argparse.ArgumentParser(description="Enrich manifest with FTM predictions")
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force regeneration of all predictions even if they already exist"
    )
    args = parser.parse_args()

    base_dir = "training_data"
    manifest_path = os.path.join(base_dir, "manifest_w_lang.json")
    
    try:
        enrich_manifest_with_ftm(
            manifest_path=manifest_path,
            base_dir=base_dir,
            force=args.force
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


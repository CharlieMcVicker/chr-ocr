#!/usr/bin/env python3
"""
This module processes a training dataset manifest and enriches it by predicting
the language (Cherokee, English, or Mix) of each image using OCR and text classification.
It updates or creates an enriched manifest `manifest_w_lang.json` while allowing
for process resumption.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.layout import add_predicted_lang_to_manifest


def main():
    base_dir = "training_data"
    manifest_path = os.path.join(base_dir, "manifest.json")
    out_manifest_path = os.path.join(base_dir, "manifest_w_lang.json")
    
    try:
        add_predicted_lang_to_manifest(
            manifest_path=manifest_path,
            out_manifest_path=out_manifest_path,
            base_dir=base_dir
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
This module filters the training manifest to clean and retain high-quality dataset entries.
It processes entries in parallel, performs Tesseract OCR on unlabeled samples, classifies
their language content, and filters out short or low-quality transcriptions.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.operations import filter_manifest

def main():
    """
    Main entry point to back up the manifest, run parallelized filtering of items
    using ThreadPoolExecutor, display processing statistics, and overwrite the JSON file.
    """
    parser = argparse.ArgumentParser(description="Filter manifest items based on OCR/classification.")
    parser.add_argument("--manifest", default="training_data/manifest.json", help="Path to manifest file")
    parser.add_argument("--image-dir", default="training_data", help="Directory where image files are located")
    args = parser.parse_args()

    manifest_path = args.manifest
    image_dir = args.image_dir
    
    # Delegate to modular library function
    filter_manifest(manifest_path=manifest_path, image_dir=image_dir)

if __name__ == "__main__":
    main()

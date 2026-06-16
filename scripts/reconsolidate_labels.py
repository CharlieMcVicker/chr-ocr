#!/usr/bin/env python3
"""
This module maps old training labels to newly created line crop manifest entries using fuzzy text matching.
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.operations import reconsolidate_labels

def main():
    parser = argparse.ArgumentParser(description="Map old training labels to new line crops using fuzzy text matching.")
    parser.add_argument("--old-manifest", default="training_data/manifest.json")
    parser.add_argument("--new-manifest", default="training_data/manifest.json")
    args = parser.parse_args()

    reconsolidate_labels(
        old_manifest_path=args.old_manifest,
        new_manifest_path=args.new_manifest
    )

if __name__ == "__main__":
    main()

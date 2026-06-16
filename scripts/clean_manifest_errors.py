#!/usr/bin/env python3
"""
Clean error entries from manifest files.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.operations import clean_manifest_errors

if __name__ == "__main__":
    paths = ["training_data/manifest_w_lang.json", "training_data/manifest.json"]
    clean_manifest_errors(paths)

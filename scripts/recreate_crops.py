#!/usr/bin/env python3
"""
Recreate crop files on disk from the newspaper page scans based on manifest coordinates.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.crops import recreate_missing_crops

if __name__ == "__main__":
    manifests = ["training_data/manifest_w_lang.json", "training_data/manifest.json"]
    recreate_missing_crops(manifest_paths=manifests)

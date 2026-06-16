#!/usr/bin/env python3
"""
Migrate crop files from older symlink structures to a standard directory.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.crops import migrate_v2_crops

if __name__ == "__main__":
    manifest_path = "training_data/manifest_w_lang.json"
    migrate_v2_crops(manifest_path=manifest_path)

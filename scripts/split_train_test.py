"""
This module splits pre-generated Tesseract training files (.png, .gt.txt, and .box)
into partitioned train (80%) and test (20%) directories to evaluate model accuracy.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from phoenix.manifest.operations import split_data

if __name__ == "__main__":
    split_data(
        "training_data/dataset/train/",
        "training_data/dataset/train_80/",
        "training_data/dataset/test_20/"
    )

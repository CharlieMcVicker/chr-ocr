"""
This module splits pre-generated Tesseract training files (.png, .gt.txt, and .box)
into partitioned train (80%) and test (20%) directories to evaluate model accuracy.
"""
import os
import random
import shutil
from pathlib import Path

def split_data(src_dir, train_dir, test_dir, split_ratio=0.8, seed=42):
    """
    Randomly splits line assets (images, ground-truths, and boxes) into distinct
    train and test groups based on a given ratio, copying the matching file triplets.
    
    Args:
        src_dir: Root directory of compiled dataset items.
        train_dir: Destination path for the training partition.
        test_dir: Destination path for the test partition.
        split_ratio: Proportion of assets allocated to train (default: 0.8).
        seed: Random seed for partition reproducibility.
    """
    random.seed(seed)
    
    src_path = Path(src_dir)
    train_path = Path(train_dir)
    test_path = Path(test_dir)
    
    train_path.mkdir(parents=True, exist_ok=True)
    test_path.mkdir(parents=True, exist_ok=True)
    
    png_files = sorted(list(src_path.glob("*.png")))
    random.shuffle(png_files)
    
    split_idx = int(len(png_files) * split_ratio)
    train_files = png_files[:split_idx]
    test_files = png_files[split_idx:]
    
    print(f"Total PNG files: {len(png_files)}")
    print(f"Training files: {len(train_files)}")
    print(f"Testing files: {len(test_files)}")
    
    for files, target_dir in [(train_files, train_path), (test_files, test_path)]:
        for png_file in files:
            # Copy PNG
            shutil.copy2(png_file, target_dir / png_file.name)
            # Copy GT.TXT
            gt_file = png_file.with_suffix(".gt.txt")
            if gt_file.exists():
                shutil.copy2(gt_file, target_dir / gt_file.name)
            # Copy BOX
            box_file = png_file.with_suffix(".box")
            if box_file.exists():
                shutil.copy2(box_file, target_dir / box_file.name)

if __name__ == "__main__":
    split_data(
        "training_data/dataset/train/",
        "training_data/dataset/train_80/",
        "training_data/dataset/test_20/"
    )

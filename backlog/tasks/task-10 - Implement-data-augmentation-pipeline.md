---
id: TASK-10
title: Implement data augmentation pipeline
status: To Do
assignee: []
created_date: '2026-06-10 19:06'
updated_date: '2026-06-11 00:00'
labels: []
dependencies: []
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Augment the base dataset using rotation, noise, and multiple binarization algorithms to improve robustness on damaged print documents.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement rotation and noise augmentation
- [ ] #2 Implement binarization augmentation (e.g. Doxa algorithms)
- [ ] #3 Generate augmented dataset
- [ ] #4 Normalize line heights to standard size AFTER augmentation
<!-- AC:END -->



## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Goal Description

The goal of Task-10 is to split our base ground-truth dataset into a training and testing set, and then build a data augmentation pipeline. For the training set, we will apply rotation, noise, and various binarization techniques (Otsu, SU, Sauvola, Wolf) to create a robust fine-tuning dataset. For the test set, we will create separate evaluation sets for each binarization algorithm to determine which preprocessing yields the best accuracy.

## Proposed Changes

We will create a Python script that first splits the base dataset (e.g., 80% train, 20% test) and then processes each set accordingly.

### Scripts

#### [NEW] [augment_dataset.py](file:///Users/charlesmcvicker/code/phoenix/scripts/augment_dataset.py)
This script will:
1. Load all original `.png` and `.gt.txt` pairs from the `dataset/ground-truth/` directory.
2. **Train/Test Split:** Randomly split the examples into `train` and `test` lists (e.g., an 80/20 or 90/10 split).
3. **Training Data Augmentation:**
   - Apply geometric and noise augmentations using OpenCV/numpy (slight rotations between -2 and +2 degrees, Gaussian/salt-and-pepper noise).
   - Apply our multiple binarization algorithms (Otsu, Sauvola, Wolf, SU) to both the original and noisy versions.
   - Save the augmented training images into `dataset/train/`, duplicating the `.gt.txt` label for each variation.
4. **Test Data Binarization:**
   - To figure out which binarization works best in production, we will apply the different binarization algorithms to the test set *without* the geometric/noise augmentations.
   - Save the test sets into organized folders (e.g., `dataset/test/base/`, `dataset/test/otsu/`, `dataset/test/sauvola/`, etc.) with their `.gt.txt` files so we can run independent validation on each preprocessing method.

## Verification Plan

### Automated Tests
- N/A

### Manual Verification
- Run `python scripts/augment_dataset.py`.
- Verify the train/test split successfully prevents test examples from appearing in the `dataset/train/` folder.
- Verify `dataset/train/` contains heavily augmented examples.
- Verify `dataset/test/` contains subdirectories for each binarization method, containing clean test examples for precise evaluation.
<!-- SECTION:PLAN:END -->

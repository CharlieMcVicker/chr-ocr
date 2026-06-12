---
id: TASK-43
title: Improve Data Augmentation
status: To Do
assignee: []
created_date: '2026-06-12 02:15'
updated_date: '2026-06-12 02:31'
labels: []
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Research and implement advanced data augmentation techniques to improve OCR model robustness and generalize better to unconstrained, noisy document layouts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement sensor noise simulations (Blur, JPEG compression, lighting shadows)
- [ ] #2 Implement spatial distortions (Grid Distortion, advanced Elastic Transform)
- [ ] #3 Implement occlusion techniques (Cutout, Random Erasing, Mixup)
- [ ] #4 Implement weakly-supervised synthetic error injection
- [ ] #5 Implement a Python-based Staged Epoch Loop supervisor script for dynamic augmentation generation and Tesseract model training
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Implement Staged Epoch Loop for Tesseract Data Augmentation

We need to transition our data augmentation strategy from a massive offline static dataset to a simulated "online" pipeline using a Staged Epoch Loop. Since Tesseract requires compiled `.lstmf` files prior to training, we will build a Python supervisor script that repeatedly generates diverse, randomized augmented data, compiles it, runs a limited number of training iterations, and cleans up the disk.

## User Review Required

> [!IMPORTANT]
> **Dependency Addition:** This plan introduces a dependency on `albumentations` for advanced image perturbation. I will need to update our environment/requirements to include this.

## Open Questions
- None right now, the plan is aligned with previous feedback!

## Proposed Changes

### `scripts/train_staged.py`
[NEW] A new python supervisor script that orchestrates the Staged Epoch Loop.
- Will accept parameters like `--total_epochs`, `--iterations_per_epoch`, `--train_manifest`, and `--variations_per_image`.
- **Data Splitting Integrity:** Ensures that augmentation *only* happens to the `train_manifest`. Test sets remain strictly untouched and unaugmented to prevent data leakage.
- Core Loop: For `epoch` in `total_epochs`:
  1. **Generate**: Run the augmentation script to generate a small configurable batch (e.g. 2-3) of randomized variations per source image in a temporary epoch-specific directory. This increases epoch density without exploding disk space.
  2. **Compile**: Run `tesseract` to convert these temporary images into `.lstmf` files and generate the `list.train` file.
  3. **Train**: Run `lstmtraining` using the `--continue_from` flag pointing to the latest checkpoint, training for `iterations_per_epoch` steps.
  4. **Cleanup**: Delete the temporary images and `.lstmf` files to save disk space before the next epoch begins.

### `scripts/augment_dynamic.py`
[NEW] A new script focused on applying random perturbations dynamically using modern tools.
- Integrates `Albumentations` to apply:
  - Sensor noise: Blur, JPEG compression artifacts, brightness/contrast jitter, lighting shadows.
  - Spatial distortions: Grid Distortion, advanced Elastic Transform.
  - Occlusion techniques: Cutout, Random Erasing.
- Processes a training manifest and outputs exactly `variations_per_image` randomized augmented images for each entry.

## Verification Plan

### Automated Tests
- N/A for this infrastructure change.

### Manual Verification
- A new task (TASK-45) has been created to formally evaluate this new pipeline.
- We will keep `train_v2.sh` and `augment_dataset.py` intact as legacy baseline tools.
- We will run `train_staged.py` and compare the validation metrics/training curves against the legacy pipeline to identify where overfitting occurs and to confirm that the new approach is substantially better. If it is, the legacy tools will be deprecated.
<!-- SECTION:PLAN:END -->

---
id: TASK-90.2
title: Update training and dynamic augmentation scripts for mixed dataset
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 19:07'
updated_date: '2026-06-17 19:15'
labels: []
dependencies: []
parent_task_id: TASK-90
ordinal: 98000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor scripts/augment_dynamic.py, scripts/augment_dataset.py, and scripts/train_staged.py to read the 'split' field from the manifest, and ensure that New Testament lines skip binarization during the staged augmentation pipeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify scripts/augment_dynamic.py and scripts/augment_dataset.py to split based on manifest 'split' field if present
- [x] #2 Skip binarization augmentation for CNT line crops, keeping them in their native binarized/grayscale form
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Refactor the training and data augmentation pipelines to respect the 'split' field in the manifest and bypass binarization for CNT data:
1. Modify scripts/augment_dynamic.py and scripts/augment_dataset.py to check if a manifest item has a pre-assigned 'split' field. If yes, respect this field to determine train/test membership instead of dynamically splitting with the accumulator. Change default split to 0.8.
2. In both files, implement a clean 'should_skip_binarization(item)' helper function (e.g. check if it has 'dataset': 'cnt' or starts with 'cnt_') to skip the binarization logic and instead keep the crop in its native grayscale/binarized form (just normalizing the height/padding) without passing a magic string deeper than needed.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored scripts/augment_dynamic.py and scripts/augment_dataset.py: Changed default split to 0.8; respected pre-assigned 'split' manifest attribute; implemented  to keep CNT dataset line crops in native grayscale/binarized form, skipping standard grid/dynamic binarizations and albumentations augmentations/bleedthrough.
<!-- SECTION:FINAL_SUMMARY:END -->

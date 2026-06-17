---
id: TASK-90.2
title: Update training and dynamic augmentation scripts for mixed dataset
status: To Do
assignee: []
created_date: '2026-06-17 19:07'
updated_date: '2026-06-17 19:08'
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
- [ ] #1 Modify scripts/augment_dynamic.py and scripts/augment_dataset.py to split based on manifest 'split' field if present
- [ ] #2 Skip binarization augmentation for CNT line crops, keeping them in their native binarized/grayscale form
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Refactor the training and data augmentation pipelines to respect the 'split' field in the manifest and bypass binarization for CNT data: 1. Modify scripts/augment_dynamic.py and scripts/augment_dataset.py to check if a manifest item has a pre-assigned 'split' field. If yes, respect this field to determine train/test membership instead of dynamically splitting with the accumulator. 2. In both files, check if the item is part of the CNT dataset (e.g. if the item ID starts with 'cnt_' or has 'dataset': 'cnt'). If it is a CNT item, skip the binarization logic (which applies Otsu, Su, Sauvola, or Wolf dynamically) and instead keep the crop in its native grayscale/binarized form (just normalizing the height/padding).
<!-- SECTION:PLAN:END -->

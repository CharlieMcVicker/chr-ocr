---
id: TASK-90
title: Generate mixed CNT/Phoenix training dataset and run OCR training
status: To Do
assignee: []
created_date: '2026-06-17 19:06'
updated_date: '2026-06-17 19:08'
labels: []
dependencies: []
ordinal: 95000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate a combined training/test OCR dataset by mixing the full Phoenix dataset with a stable 10% random sample from each Cherokee New Testament (CNT) book. Redo the test/validation splits beforehand to keep the Phoenix test set stable, ensure CNT lines skip binarization augmentation, and train a new model using the staged data augmentation pipeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement stable random sampling of each CNT book using a standard key/salt and book number
- [ ] #2 Tune random sampling to 10% of CNT lines (about size of Phoenix dataset)
- [ ] #3 Redo test/validation split, keeping Phoenix test set stable by splitting CNT before mixing
- [ ] #4 Skip binarization augmentation for CNT data during staged data augmentation training
- [ ] #5 Run staged data augmentation training pipeline on the mixed dataset with extra epochs
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Generate a combined training/test OCR dataset by mixing the full Phoenix dataset with a stable 10% random sample from each CNT book (tuning the fraction if needed). Split the datasets beforehand to ensure that the Phoenix test set remains stable. The CNT test splits will be placed in a separate evaluation directory (training_data/dataset/test/cnt/) so that we can evaluate performance separately on Phoenix-only and CNT-only splits (doing a weighted sum of error rates based on example count). Update the training and dynamic augmentation scripts to skip binarization augmentation for CNT line crops.
<!-- SECTION:PLAN:END -->

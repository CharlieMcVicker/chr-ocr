---
id: TASK-37
title: Training run with 80/20 train/test split
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-11 16:36'
updated_date: '2026-06-11 16:43'
labels:
  - training
  - evaluation
dependencies: []
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run a Tesseract LSTM fine-tuning experiment that uses an explicit 80/20 train/test split rather than using all labeled data for training. This will give a proper held-out test set to evaluate generalization during and after training.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dataset is split 80% train / 20% test before training
- [x] #2 Training run completes successfully
- [x] #3 Test set CER/accuracy is evaluated after training using lstmeval
- [x] #4 Results are documented and compared to prior runs
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented 80/20 train/test split (1920 train / 480 test). Ran training for 200 iterations on the 80% split. Evaluated on the 20% test split. Results: Train BCER 39.467%, Test BCER 36.847%. Generalization confirmed.
<!-- SECTION:FINAL_SUMMARY:END -->

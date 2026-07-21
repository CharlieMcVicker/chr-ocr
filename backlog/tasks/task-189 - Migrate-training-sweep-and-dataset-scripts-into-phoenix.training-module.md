---
id: TASK-189
title: 'Migrate training, sweep, and dataset scripts into phoenix.training module'
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 16:13'
updated_date: '2026-07-21 16:37'
labels: []
dependencies: []
ordinal: 197000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move train_staged.py, augment_dynamic.py, augment_dataset.py, evaluate_mixed_model.py, evaluate_checkpoints.py, mix_datasets.py, pre_augment_cnt.py, and tune_meta_parameters.py into phoenix/training and update all import callers across the repo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move training scripts into phoenix/training/
- [x] #2 Update python references in phoenix/training/sweep.py, train.py, eval.py, etc.
- [x] #3 Pass all tests
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully migrated training, sweep, and dataset scripts (train_staged.py, augment_dynamic.py, augment_dataset.py, evaluate_mixed_model.py, evaluate_checkpoints.py, mix_datasets.py, pre_augment_cnt.py, tune_meta_parameters.py) into phoenix/training/ module, updated internal Python references across phoenix/training/ (sweep.py, train.py, eval.py, etc.) to point to phoenix/training/ module paths, and verified all pytest test suites pass cleanly.
<!-- SECTION:FINAL_SUMMARY:END -->

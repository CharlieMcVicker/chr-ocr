---
id: TASK-160
title: Allow skipping CNT evaluation in second phase training
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-22 22:37'
updated_date: '2026-06-22 22:40'
labels: []
dependencies: []
priority: high
ordinal: 181000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce a skip_cnt_eval configuration flag to skip the expensive CNT test set evaluation during the second phase of training and hyperparameter sweeps, while keeping it enabled for pre-training checkpoint selection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add skip_cnt_eval field to TrainingConfig in phoenix/config.py
- [x] #2 Add --skip-cnt option to scripts/evaluate_mixed_model.py to conditionally bypass evaluating the CNT test set
- [x] #3 Update evaluate_checkpoint in phoenix/training/eval.py to pass skip_cnt flag to evaluate_mixed_model.py
- [x] #4 Update train_staged.py and sweep.py to pass skip_cnt_eval from config/experiment config
- [x] #5 Set skip_cnt_eval to true in sweep configurations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented skip_cnt_eval in TrainingConfig, evaluate_mixed_model.py, eval.py, train_staged.py, and sweep.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added skip_cnt_eval configuration flag and --skip-cnt option to bypass CNT evaluation during fine-tuning/sweeps. Verified functionality.
<!-- SECTION:FINAL_SUMMARY:END -->

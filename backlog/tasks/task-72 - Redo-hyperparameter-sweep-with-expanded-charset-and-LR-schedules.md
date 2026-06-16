---
id: TASK-72
title: Redo hyperparameter sweep with expanded charset and LR schedules
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 19:39'
updated_date: '2026-06-16 20:55'
labels: []
dependencies: []
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Redo the hyperparameter tuning sweep on the post-fix model with the expanded charset, evaluating longer training runs, different learning rate schedules, and various augmentation intensities.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify training scripts to support customizable learning rate schedules (e.g. step decay)
- [x] #2 Define and execute a sweep matrix of at least 4 runs comparing different schedules and run lengths
- [x] #3 Identify the optimal configuration and document the findings in a research doc
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully completed the hyperparameter tuning sweep on the expanded charset model. Modified scripts/train_staged.py to support step and exp decay schedules. Conducted a sweep of 6 runs (runs 17 to 22) to evaluate longer epochs, schedules, and augmentation amounts. Identified run 20 (20 epochs, constant 0.0005 LR) as the new best model with a record low 7.033% BCER, and run 21 (16 epochs, step decay, moderate/halved augmentation) as the best configuration for word-level accuracy (14.752% BWER). Updated doc-9 and doc-11 with these findings.
<!-- SECTION:FINAL_SUMMARY:END -->

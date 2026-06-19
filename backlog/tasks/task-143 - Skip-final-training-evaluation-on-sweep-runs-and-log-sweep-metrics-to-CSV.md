---
id: TASK-143
title: Skip final training evaluation on sweep runs and log sweep metrics to CSV
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 21:06'
updated_date: '2026-06-19 21:07'
labels: []
dependencies: []
priority: high
ordinal: 161000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add skip_final_eval boolean to TrainingConfig to skip final 5-epoch evaluation in train_staged.py during sweeps. Enable this in the sweep coordinator, and ensure that the sweep's evaluation statistics are appended to the run's epoch_metrics.csv file on disk.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add skip_final_eval boolean to TrainingConfig with default False
- [x] #2 In train_staged.py, skip evaluate_and_update_best if skip_final_eval is True
- [x] #3 In sweep.py, set skip_final_eval to True on experiment configs
- [x] #4 In sweep.py, write the sweep evaluation metrics to epoch_metrics.csv
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented skip_final_eval in TrainingConfig and updated train_staged.py and sweep.py to skip final evaluation from training run and move it to the sweeper, ensuring metrics are logged to the run's CSV file on disk.
<!-- SECTION:FINAL_SUMMARY:END -->

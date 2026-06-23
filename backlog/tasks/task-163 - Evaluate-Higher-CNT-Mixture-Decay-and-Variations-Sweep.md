---
id: TASK-163
title: Evaluate Higher CNT Mixture Decay and Variations Sweep
status: Done
assignee:
  - '@myself'
created_date: '2026-06-22 23:21'
updated_date: '2026-06-22 23:22'
labels: []
dependencies: []
priority: high
ordinal: 184000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a sweep configuration starting with a higher Cherokee New Testament (CNT) ratio (30% reducing to 5% by epoch 16) and evaluating different numbers of image variations (3, 5, 7) to find a more optimal fine-tuning mixture schedule.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create configs/sweep_task_163_cnt_decay.json with 30% CNT decaying to 5% CNT at epoch 16
- [x] #2 Define experiments evaluating 3, 5, and 7 variations per image
- [x] #3 Configure base fine-tuning learning rate at 0.001 with exponential decay
- [x] #4 Kick off the background sweep execution and report the run details
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Successfully created configs/sweep_task_163_cnt_decay.json containing the 30% decaying to 5% CNT schedule across 16 epochs, evaluating 3, 5, and 7 variations per image, with an initial learning rate of 0.001. Kicked off the sweep run in the background (Task ID: task-48).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully created a new variation on the recent best configuration (configs/sweep_task_163_cnt_decay.json). It implements a mixture schedule decay starting at 30% CNT (0.70 Phoenix ratio) and linear decaying to 5% CNT (0.95 Phoenix ratio) by epoch 16. It also evaluates 3, 5, and 7 variations per image to find the optimal combination. Kicked off the sweep run in the background (Task ID: task-48).
<!-- SECTION:FINAL_SUMMARY:END -->

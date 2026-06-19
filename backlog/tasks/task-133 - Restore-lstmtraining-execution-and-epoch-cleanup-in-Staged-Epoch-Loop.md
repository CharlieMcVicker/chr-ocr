---
id: TASK-133
title: Restore lstmtraining execution and epoch cleanup in Staged Epoch Loop
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 16:56'
updated_date: '2026-06-19 17:00'
labels: []
dependencies: []
ordinal: 151000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Staged Epoch Loop in phoenix/training/train.py has accidentally omitted Steps D, E, and F (which invoke lstmtraining and perform cleanup) across pool-shared and non-shared branches. This task restores the missing steps to run actual training.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Steps D, E, and F are restored to the staged training loop in phoenix/training/train.py
- [x] #2 A dry-run sweep configuration check succeeds
- [x] #3 A short minimal-epoch training test successfully writes checkpoints to the output directory
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Restored Steps D, E, and F (checkpoint continuation, learning rate scheduling, lstmtraining invocation, and directory cleanup) to phoenix/training/train.py. This ensures that the Staged Epoch Loop successfully runs Tesseract training, writes checkpoint files, and cleans up temporary files without touching the shared pool directory. Verified successfully with dry-run and physical execution tests.
<!-- SECTION:FINAL_SUMMARY:END -->

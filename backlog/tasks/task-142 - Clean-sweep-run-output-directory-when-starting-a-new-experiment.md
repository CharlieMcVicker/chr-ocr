---
id: TASK-142
title: Clean sweep run output directory when starting a new experiment
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 19:04'
updated_date: '2026-06-19 19:05'
labels: []
dependencies: []
priority: high
ordinal: 160000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a training sweep begins testing a new config, ensure the previous run output directory for that experiment config is fully cleaned/deleted so old logs, metrics, and checkpoints do not contaminate the new results.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Delete the run output directory if it exists before running the staged training command
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Modified phoenix/training/sweep.py to import shutil and cleanly delete both the existing run output directory and the temporary epoch directories before starting staged training for any experiment in the sweep matrix. This guarantees that old log files, checkpoints, and metrics CSVs do not contaminate the new run results.
<!-- SECTION:FINAL_SUMMARY:END -->

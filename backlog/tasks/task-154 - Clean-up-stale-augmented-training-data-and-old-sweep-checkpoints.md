---
id: TASK-154
title: Clean up stale augmented training data and old sweep checkpoints
status: Done
assignee:
  - '@myself'
created_date: '2026-06-22 14:17'
updated_date: '2026-06-22 14:18'
labels: []
dependencies: []
priority: low
ordinal: 175000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove stale generated augmented datasets and checkpoint folders from previous training runs and sweeps to reclaim disk space.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify and remove old augmented dynamic data subdirectories under training_data/ (>4 days old)
- [x] #2 Identify and remove stale checkpoints under training_data/staged_tuning/ (>4 days old) that are not referenced by any best model config
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reclaimed ~3 GB of space by identifying and removing stale training datasets (>4 days old) and obsolete, unreferenced sweep checkpoints older than 4 days under training_data/.
<!-- SECTION:FINAL_SUMMARY:END -->

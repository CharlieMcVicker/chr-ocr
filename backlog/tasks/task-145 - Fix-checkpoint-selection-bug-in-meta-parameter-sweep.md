---
id: TASK-145
title: Fix checkpoint selection bug in meta-parameter sweep
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 22:29'
updated_date: '2026-06-19 22:30'
labels: []
dependencies: []
modified_files:
  - phoenix/training/sweep.py
priority: medium
ordinal: 163000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Correct the checkpoint lookup logic in sweep.py to use the actual checkpoint iteration (group 1) instead of the max iterations parameter (group 2).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify get_checkpoint_for_epoch in sweep.py to use match.group(1)
- [x] #2 Verify that checkpoint selection functions correctly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Corrected the checkpoint selection lookup logic in get_checkpoint_for_epoch of phoenix/training/sweep.py to parse match.group(1) (the actual checkpoint iteration) instead of match.group(2) (the run's total/max iterations). Created a robust unit test suite under phoenix/training/test_sweep_checkpoint.py verifying both exact checkpoint matching and closest checkpoint iteration fallback logic, which now successfully passes.
<!-- SECTION:FINAL_SUMMARY:END -->

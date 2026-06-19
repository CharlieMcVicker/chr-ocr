---
id: TASK-139
title: Consolidate and streamline training sweeps to direct-line mixed evaluation
status: Done
assignee:
  - '@subagent'
created_date: '2026-06-19 18:32'
updated_date: '2026-06-19 18:33'
labels:
  - cleanup
  - sweeps
  - evaluation
dependencies: []
ordinal: 157000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the old bcer/lstmeval evaluation mode and make the direct-line mixed mode (CER/WER calculation with Cherokee-specific NFC and casing normalization) the default and only evaluation behavior across all training sweeps.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove the old evaluate_checkpoint_bcer function from phoenix/training/sweep.py
- [x] #2 Update run_meta_parameter_sweep in sweep.py to use direct-line mixed mode evaluation by default and remove the eval_mode parameter
- [x] #3 Remove --eval-mode argument from scripts/tune_meta_parameters.py and update path/results-file defaults to assume mixed evaluation
- [x] #4 Verify that a dry-run sweep runs successfully with no errors
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify phoenix/training/sweep.py to remove evaluate_checkpoint_bcer and remove eval_mode parameter.\n2. Modify scripts/tune_meta_parameters.py to remove --eval-mode CLI option and update defaults to target training_data/dataset and chr.traineddata directly.\n3. Run a dry-run to verify.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Consolidated training sweeps to always perform direct-line mixed evaluation, completely deprecating and removing obsolete bcer/lstmeval evaluation mode. Updated training sweep.py and tune_meta_parameters.py script, verified via a successful dry-run with new defaults.
<!-- SECTION:FINAL_SUMMARY:END -->

---
id: TASK-117
title: Fix mixed model sweep evaluation feedback and saved config optimal epochs
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 23:38'
updated_date: '2026-06-18 23:39'
labels: []
dependencies: []
ordinal: 131000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve usability and clarity of sweep_mixture_ratios.py by adding epoch labels to evaluation printouts and updating configs/train_mixed.json with the optimal epoch value.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 sweep_mixture_ratios.py prints the epoch/checkpoint details in a header preceding each subprocess call to evaluate_mixed_model.py
- [x] #2 configs/train_mixed.json is saved with total_epochs updated to the optimal epoch identified by the sweep
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify scripts/sweep_mixture_ratios.py to print a prominent header identifying the epoch/checkpoint being evaluated.\n2. Modify scripts/sweep_mixture_ratios.py to set total_epochs in the optimal config (best_exp.config) to the best run's epoch number before saving to configs/train_mixed.json.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated scripts/sweep_mixture_ratios.py to print prominent headers identifying each epoch during evaluation subprocess runs, and ensured that the saved optimal configuration (configs/train_mixed.json) has its total_epochs value updated to the best run's epoch number.
<!-- SECTION:FINAL_SUMMARY:END -->

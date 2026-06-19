---
id: TASK-116
title: Modularize Checkpoint Evaluation & Track Best Scorers
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 21:47'
updated_date: '2026-06-18 21:52'
labels: []
dependencies: []
ordinal: 130000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor checkpoint evaluation, slicing, and best-model tracking into a reusable python module, supporting custom checkpoint slicing and tracking best-performers for both Phoenix CER and Weighted CER.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create modular eval.py functions
- [x] #2 Implement evaluate_checkpoints.py supporting slicing
- [x] #3 Update train_staged.py to use eval.py
- [x] #4 Support separate best_model directories for phoenix and weighted
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Modularized the checkpoint evaluation, compilation, slicing, and metrics tracking into a reusable phoenix/training/eval.py module. Implemented the scripts/evaluate_checkpoints.py CLI tool, replacing evaluate_top_n.py and adding custom slice syntax support. Replaced duplicated inline logic in scripts/train_staged.py with eval.py calls, and implemented tracking best models for both Phoenix CER and Weighted CER metrics into best_model/phoenix/ and best_model/weighted/ subdirectories.
<!-- SECTION:FINAL_SUMMARY:END -->

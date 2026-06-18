---
id: TASK-114
title: Track and maintain best model checkpoint and config in project root
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-18 20:36'
updated_date: '2026-06-18 20:37'
labels: []
dependencies: []
priority: high
ordinal: 128000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update train_staged or create a wrapper to run training and evaluation, maintaining the best config, best checkpoint, and scoring stats.json in a folder at the project root.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create 'best_model' folder at the project root if it does not exist
- [x] #2 Integrate evaluation at the end of train_staged or via a wrapper
- [x] #3 Compare evaluated CER against current best model stored in the project root folder
- [x] #4 If the new model is better (or if no best model exists), copy its checkpoint, config, and stats.json to the folder
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated scripts/train_staged.py to automatically evaluate the final checkpoint after training completes. The script compiles the checkpoint to a temporary .traineddata, runs evaluate_mixed_model.py, parses the metrics, and maintains a 'best_model/' directory at the project root. This directory tracks 'best_config.json', 'best.checkpoint', 'best.traineddata', and 'scoring_stats.json' based on the lowest overall Weighted Mean CER.
<!-- SECTION:FINAL_SUMMARY:END -->

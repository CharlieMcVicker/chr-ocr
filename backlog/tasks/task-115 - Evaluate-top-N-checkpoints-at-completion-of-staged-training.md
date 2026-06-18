---
id: TASK-115
title: Evaluate top N checkpoints at completion of staged training
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-18 20:40'
updated_date: '2026-06-18 20:41'
labels: []
dependencies: []
priority: high
ordinal: 129000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enhance the post-training evaluation logic in train_staged.py to evaluate the last N checkpoints (e.g., top 5) sorted by iteration number, find the best performing checkpoint among them (lowest CER), and save it in best_model/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Find all checkpoints in the train_output_dir
- [x] #2 Sort checkpoints by iteration number and select the top N (default 5)
- [x] #3 Compile and evaluate each of the top N checkpoints
- [x] #4 Identify the best performer and update 'best_model/' with its config, checkpoint, compiled model, and stats
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Enhanced evaluation logic to read all checkpoints from the training output directory, sort them by iteration number, and select the top 5 (last 5 epochs/iterations). Each of these 5 checkpoints is unpacked to its own temporary .traineddata, evaluated, and the peak performing checkpoint of the run (lowest weighted CER) is determined. It is then compared to the previous global best in best_model/, updating the best config, best checkpoint, best compiled model, and stats accordingly.
<!-- SECTION:FINAL_SUMMARY:END -->

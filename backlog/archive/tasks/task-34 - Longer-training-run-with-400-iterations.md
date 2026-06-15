---
id: TASK-34
title: Longer training run with 400 iterations
status: Done
assignee: []
created_date: '2026-06-11 15:05'
updated_date: '2026-06-11 15:10'
labels: []
dependencies: []
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run a longer training run with 400 iterations, ensuring results are kept in addition to existing training data. Update training script to take iterations as an argument. Analyze if overfitting was reached.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated scripts/train_v2.sh and scripts/evaluate_v2.sh to support an iterations argument and unique timestamped output directories. Ran 400 iterations, which showed overfitting after ~200 iterations. Confirmed with a clean 200-iteration run hitting the peak BCER of 34.490% on the evaluation set.
<!-- SECTION:FINAL_SUMMARY:END -->

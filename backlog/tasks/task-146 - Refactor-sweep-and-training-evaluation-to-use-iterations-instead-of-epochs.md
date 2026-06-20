---
id: TASK-146
title: Refactor sweep and training evaluation to use iterations instead of epochs
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 22:31'
updated_date: '2026-06-19 22:39'
labels: []
dependencies: []
priority: high
ordinal: 164000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stop using epochs as the indexing unit for checkpoints and evaluation in the hyperparameter sweep and training pipelines, switching to direct iteration counts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support eval_iterations in SweepConfig and ExperimentConfig instead of eval_epochs
- [x] #2 Update sweep.py to look up checkpoints and log results using iteration numbers directly
- [x] #3 Update scripts/train_staged.py and training_data metrics to use iterations instead of epoch-by-epoch indexing
<!-- AC:END -->

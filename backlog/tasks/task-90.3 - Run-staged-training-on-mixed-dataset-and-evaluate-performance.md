---
id: TASK-90.3
title: Run staged training on mixed dataset and evaluate performance
status: To Do
assignee: []
created_date: '2026-06-17 19:07'
updated_date: '2026-06-17 19:08'
labels: []
dependencies: []
parent_task_id: TASK-90
ordinal: 99000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Execute the staged training loop with the mixed manifest using optimal settings and extra epochs. Packages the best checkpoint and evaluates it on the test sets to report CER/WER metrics.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Run train_staged.py using the mixed manifest for extra epochs (e.g. 15-20 epochs)
- [ ] #2 Convert best checkpoint into a traineddata file
- [ ] #3 Evaluate model against Phoenix and CNT test splits and generate comparative performance reports
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Run training and evaluate performance with separated evaluation metrics: 1. Execute scripts/train_staged.py using --train-manifest training_data/manifest_mixed.json with extra epochs (e.g. 15 or 20 epochs) due to the much larger dataset size. 2. Package the best checkpoint into chr_best_finetuned.traineddata using the lstmtraining --stop_training command. 3. Package the test datasets and evaluate the fine-tuned model against: - The original Phoenix test set (test/base and the binarized splits) - The CNT test set (test/cnt/) 4. Compute and log independent error rates (BCER, BWER) for both Phoenix and CNT datasets, then compute a weighted sum based on the number of examples to assess overall combined performance.
<!-- SECTION:PLAN:END -->

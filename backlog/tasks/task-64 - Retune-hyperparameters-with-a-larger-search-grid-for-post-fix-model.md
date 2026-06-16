---
id: TASK-64
title: Retune hyperparameters with a larger search grid for post-fix model
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 12:40'
updated_date: '2026-06-16 13:19'
labels: []
dependencies: []
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With the Albumentations augmentation bug resolved, the training dataset complexity has increased, resulting in a ~1.8pp degradation in BCER. We must retune the training hyperparameters (epochs, learning rate, and data augmentation metaparameters like shadow limits and noise levels) using a larger search grid to allow optimal convergence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Prepare a grid search script targeting epochs, learning rate, and Albumentations parameters
- [x] #2 Execute hyperparameter tuning sweep on the post-fix pipeline
- [x] #3 Identify the new optimal model checkpoint and document validation accuracy and BCER/BWER scores
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully completed the hyperparameter tuning sweep on the post-fix pipeline (with corrected Albumentations parameters) using an 80/20 train/test split. Exposed learning rate and Albumentations parameters across augment_dynamic.py and train_staged.py. Identified the optimal model configuration: run_14_lower_lr at epoch 12 (lr=0.0005, error_rate=0.05, epoch=12) which achieved a new low of 12.357% average BCER (and 8.233% on base clean crops). Documented findings in research/doc-11 and updated the main best_checkpoint.checkpoint model.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Verify that all training runs complete successfully
- [x] #2 Update doc-11 with new optimal parameters and metrics
- [x] #3 Verify that the final fine-tuned model checkpoint is successfully generated and validated
<!-- DOD:END -->

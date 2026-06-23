---
id: TASK-158
title: Explore Hyperparameter Space with Moderate Regularization and Learning Rates
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-22 20:33'
updated_date: '2026-06-22 21:42'
labels:
  - training
  - sweep
dependencies: []
priority: high
ordinal: 179000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure and execute a multi-experiment training sweep using the 3k pre-trained CNT checkpoint. We will explore a hyperparameter space consisting of varying learning rates (e.g., 0.0015, 0.002, 0.0025) and mixture schedule parameters with moderate regularization to find an optimal configuration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create configs/sweep_moderate_reg_lr_space.json with multiple experiments exploring learning rates and mixture schedule end-ratios.
- [x] #2 Execute the multi-experiment sweep in the background.
- [x] #3 Analyze the evaluation metrics and report outcomes.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully designed, executed, and analyzed a multi-experiment training sweep exploring moderate regularization and learning rates starting from the pre-trained 3k CNT foundation checkpoint. The sweep compared three strategies: (1) moderate learning rate with moderate regularization, (2) higher learning rate with light regularization, and (3) optimal learning rate with clean Phoenix scans and asymmetric noise strictly on CNT. All three runs converged well, achieving <9% Phoenix CER in the first 400-500 iterations. The asymmetric noise run (two_stage_opt_lr_asymmetric_noise) achieved the overall best result of 8.16% Phoenix CER at iteration 950, showing that keeping Phoenix scans pristine while regularizing the auxiliary CNT data is highly effective.
<!-- SECTION:FINAL_SUMMARY:END -->

---
id: TASK-151
title: Run Two-Phase Learning Rate and Punctuation Sweep (Task 151)
status: To Do
assignee: []
created_date: '2026-06-22 13:02'
updated_date: '2026-06-22 13:02'
labels: []
dependencies: []
priority: high
ordinal: 172000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Execute the newly proposed two-phase sweep configuration at 'configs/sweep_two_stage_lr_punctuation.json' to test higher learning rates (0.004-0.005) and targeted punctuation retention (3% residual noise with bracket-heavy samples).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Execute the sweep using the newly implemented two-phase runner
- [ ] #2 Confirm that CNT pre-training is skipped on subsequent runs if the foundational checkpoint is on disk
- [ ] #3 Analyze the resulting CER metrics for learning rates 0.004 and 0.005 to identify the new adaptation limit
- [ ] #4 Check the deletion rate of brackets '[' and ']' in the 3% mixture runs to see if targeted regularization resolved the bracket dropping issue
- [ ] #5 Write the champion configuration to best_config.json and best_checkpoint.checkpoint
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Experiment Configuration Parameters

We have created the configuration file at `configs/sweep_two_stage_lr_punctuation.json`. It specifies the following two-phase parameters:

### 1. Pre-Training Phase (CNT Foundation)
- **Epochs**: 10 (250 iterations/epoch)
- **Mixture Ratio**: 0.0 (100% CNT synthetic data)
- **Noise / Augmentations**: Heavy (smudging, high micro-dropout, multi-scale distortion, elastic warping)
- **Goal**: Create a rock-solid, highly regularized character-recognition foundation (`cnt_foundation.checkpoint`).

### 2. Fine-Tuning Phase (Phoenix Adaptation & Punctuation Regularization)
- **Epochs**: 8 (200 iterations/epoch)
- **Base Mixture Ratio**: 0.99 (1% residual CNT noise)
- **Experiments**:
  1. `two_stage_lr_003_baseline`: Fine-tuning starting from the foundation with `lr = 0.003`.
  2. `two_stage_lr_004`: Sweeping `lr = 0.004` to see if adaptation improves.
  3. `two_stage_lr_005`: Sweeping `lr = 0.005` to push limits.
  4. `two_stage_punc_heavy_lr_003`: Testing 3% residual CNT noise containing high density bracket samples with `lr = 0.003` to combat `[` and `]` deletion.
  5. `two_stage_punc_heavy_lr_004`: Testing 3% residual noise with `lr = 0.004` to balance aggressive adaptation and punctuation retention.
<!-- SECTION:PLAN:END -->

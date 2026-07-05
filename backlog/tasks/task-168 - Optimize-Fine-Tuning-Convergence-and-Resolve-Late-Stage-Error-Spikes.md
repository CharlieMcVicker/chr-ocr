---
id: TASK-168
title: Optimize Fine-Tuning Convergence and Resolve Late-Stage Error Spikes
status: To Do
assignee: []
created_date: '2026-06-24 14:38'
labels:
  - training
  - optimization
  - lr-schedule
dependencies: []
priority: high
ordinal: 189000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Address the late-stage convergence issues where training error rises or fails to recover in later epochs. This is caused by the interaction between the exponential learning rate decay and the epoch-by-epoch fresh dynamic augmentations (which suddenly present new distortions that the tiny learning rate cannot adapt to in 200 iterations).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Evaluate a learning rate schedule with a non-zero minimum learning rate (e.g., Cosine Annealing with Warmup) to prevent the LR from dropping too low to learn
- [ ] #2 Evaluate a noise decay/annealing curriculum where augmentation probabilities (e.g., distortion, blur, shadow) are gradually reduced as the training progresses
- [ ] #3 Evaluate increasing the epoch size (iterations per epoch) to allow the model more steps to adapt to new pool distributions
- [ ] #4 Compare the final performance and error curves of the revised configurations against the two_stage_lr_0010_exp_decay baseline
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Review current training loop config and scripts/train_staged.py.\n2. Formulate and implement support for noise/augmentation parameter schedules or decay.\n3. Run experimental sweeps comparing different learning rate floors (e.g., eta_min >= 0.0001) and/or noise annealing curriculum.\n4. Analyze results and select the optimal configuration.
<!-- SECTION:PLAN:END -->

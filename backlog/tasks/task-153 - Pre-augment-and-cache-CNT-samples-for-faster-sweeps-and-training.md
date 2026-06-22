---
id: TASK-153
title: Pre-augment and cache CNT samples for faster sweeps and training
status: To Do
assignee: []
created_date: '2026-06-22 13:51'
labels: []
dependencies: []
priority: medium
ordinal: 174000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Since we only use a fraction of CNT samples regularly, we can pre-augment the CNT dataset and cache the augmented images. This avoids running expensive dynamic augmentation on CPU during training and sweeps, drastically speeding up runtimes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create a script to pre-augment the CNT dataset with target heavy noise parameters.
- [ ] #2 Implement caching and loading of pre-augmented CNT samples in the training pipeline.
- [ ] #3 Verify identical model performance and significantly faster training speed.
<!-- AC:END -->

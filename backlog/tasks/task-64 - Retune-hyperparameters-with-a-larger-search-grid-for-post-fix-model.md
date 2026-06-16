---
id: TASK-64
title: Retune hyperparameters with a larger search grid for post-fix model
status: To Do
assignee: []
created_date: '2026-06-16 12:40'
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
- [ ] #1 Prepare a grid search script targeting epochs, learning rate, and Albumentations parameters
- [ ] #2 Execute hyperparameter tuning sweep on the post-fix pipeline
- [ ] #3 Identify the new optimal model checkpoint and document validation accuracy and BCER/BWER scores
<!-- AC:END -->

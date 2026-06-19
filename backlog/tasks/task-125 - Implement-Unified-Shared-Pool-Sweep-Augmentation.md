---
id: TASK-125
title: Implement Unified Shared-Pool Sweep Augmentation
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-06-19 13:15'
updated_date: '2026-06-19 14:41'
labels: []
dependencies: []
modified_files:
  - phoenix/training/sweep.py
ordinal: 139000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Optimize hyperparameter sweeps by generating a single master pool of augmented images and compiled .lstmf files per epoch, and dynamically sampling from this pool to build experiment-specific train.list files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design and implement a master-pool generator in scripts/augment_dynamic.py that saves pre-compiled .lstmf files and writes a metadata index tracking applied augmentations.
- [ ] #2 Develop a Sweep Sampler utility that reads the metadata index and filters/samples .lstmf files to construct a unique train.list matching each experiment's target probabilities.
- [ ] #3 Update the sweep runner script to run the master generation once per epoch, bypassing both image processing and Tesseract compilation for individual models.
- [ ] #4 Verify that multiple models in a sweep train successfully on different train.list files drawn from the same master pool.
- [ ] #5 Update the architectural and operational documentation of the Unified Shared-Pool Sweep Augmentation in backlog/docs/research/mixed-training-augmentation.md
<!-- AC:END -->

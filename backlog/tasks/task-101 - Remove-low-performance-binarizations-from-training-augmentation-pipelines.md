---
id: TASK-101
title: Remove low-performance binarizations from training augmentation pipelines
status: To Do
assignee: []
created_date: '2026-06-18 02:32'
labels: []
dependencies: []
ordinal: 109000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove binarization methods/parameters that yield high character error rates (specifically Su, and Sauvola with k >= 0.2) from the training data generation and dynamic augmentation pipelines based on the binarization sweep evaluation results.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Remove su binarization and sauvola with k >= 0.2 from scripts/augment_dataset.py
- [ ] #2 Remove su binarization and sauvola with k >= 0.2 from scripts/augment_dynamic.py
<!-- AC:END -->

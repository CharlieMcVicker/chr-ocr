---
id: TASK-99.3
title: Refine dynamic augmentation parameters (warping and noise rate)
status: To Do
assignee: []
created_date: '2026-06-18 02:43'
labels: []
dependencies: []
parent_task_id: TASK-99
ordinal: 111000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Optimize the intensity and range of dynamic augmentations to prevent unrealistic artifacts (like excessive warping) while improving model robustness by tuning/increasing noise rates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Reduce the range of geometric warping in dynamic augmentations to prevent crazy artifacts
- [ ] #2 Tune/increase noise rates or overall augmentation intensity (interpolating from CNT settings) in scripts/augment_dynamic.py
<!-- AC:END -->

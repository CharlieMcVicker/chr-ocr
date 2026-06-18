---
id: TASK-99.3
title: Refine dynamic augmentation parameters (warping and noise rate)
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 02:43'
updated_date: '2026-06-18 02:47'
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
- [x] #1 Reduce the range of geometric warping in dynamic augmentations to prevent crazy artifacts
- [x] #2 Tune/increase noise rates or overall augmentation intensity (interpolating from CNT settings) in scripts/augment_dynamic.py
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reduced default distortion_limit to 0.05 and elastic distortion amplitude to 1.5-3.0 in augment.py to prevent crazy warping artifacts. Adjusted default noise and distortion probabilities in config.py, augment_dynamic.py, and passed distortion_limit down to the pipelines in train.py and augment_dynamic.py.
<!-- SECTION:FINAL_SUMMARY:END -->

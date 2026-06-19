---
id: TASK-99
title: >-
  Consolidated: Improve training data quality (grayscale, optimized
  binarizations, & refined augmentations)
status: Done
assignee: []
created_date: '2026-06-17 23:55'
updated_date: '2026-06-18 02:47'
labels: []
dependencies: []
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Improve Phoenix and CNT training data quality by optimizing binarizations, introducing grayscale variations, and refining augmentation parameters.

Specifically:
1. Remove low-performance binarization methods/parameters (specifically Su, and Sauvola with k >= 0.2) from both static and dynamic augmentation pipelines.
2. Include raw, non-binarized 'grayscale' variations for Cherokee Phoenix images in both static and dynamic training data pipelines (aligning with optimal evaluation performance where native grayscale yielded the lowest CER of 4.680%).
3. Refine dynamic augmentation parameters: reduce the range of geometric warping to avoid unrealistic artifacts, and tune/increase noise rates or overall augmentation intensity (interpolating from CNT pipeline settings).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Complete subtask TASK-99.1: Remove low-performance binarizations from training pipelines
- [x] #2 Complete subtask TASK-99.2: Include raw grayscale variations for Phoenix images in training pipelines
- [x] #3 Complete subtask TASK-99.3: Refine dynamic augmentation parameters (warping and noise rate)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed all three subtasks: TASK-99.1 (removed low-performance binarizations like Su and Sauvola k>=0.2), TASK-99.2 (included grayscale native variations for training), and TASK-99.3 (refined distortion limit, elastic warp amplitude, and noise rates).
<!-- SECTION:FINAL_SUMMARY:END -->

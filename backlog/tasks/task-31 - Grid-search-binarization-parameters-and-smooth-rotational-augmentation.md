---
id: TASK-31
title: Grid-search binarization parameters and smooth rotational augmentation
status: Done
assignee: []
created_date: '2026-06-11 12:53'
updated_date: '2026-06-11 12:57'
labels: []
dependencies: []
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Increase the range of binarization parameters, smooth the rotational augmentation, and generate evaluating grids for each algorithm to find the ideal parameters.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully removed the <60px fallback in binarizer.py, implemented smooth random rotational augmentations and parameterized training dataset generation. The evaluation script now evaluates 29 different binarization/parameter configurations. Base grayscale remained the best (41.4%), while Sauvola w=35, k=0.1 was the best binarization algorithm (46.1%).
<!-- SECTION:FINAL_SUMMARY:END -->

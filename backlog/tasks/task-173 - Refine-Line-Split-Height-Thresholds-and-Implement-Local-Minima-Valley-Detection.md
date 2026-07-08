---
id: TASK-173
title: >-
  Refine Line Split Height Thresholds and Implement Local Minima Valley
  Detection
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-05 20:49'
updated_date: '2026-07-05 20:52'
labels:
  - layout
  - segmentation
dependencies: []
priority: high
ordinal: 191000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Lower the line split height threshold trigger from 1.5x target_height to 1.25x target_height (e.g. 38px) to catch tightly packed multi-line merges. Additionally, update the projection splitting algorithm to find local energy minima (peaks and valleys of line density) rather than requiring absolute near-zero whitespace valleys, allowing robust splitting when descenders and ascenders slightly overlap.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Lower the split triggering threshold in extract_lines_from_images_batch from 1.5x to 1.2x or 1.25x target_height
- [x] #2 Enhance split_merged_crop_by_projection in phoenix/layout/segmentation.py to identify local minima of projection row density when clean whitespace valleys are unavailable
- [x] #3 Test updated splitting logic on seq-3.jp2 and verify that crop col_0_line_4.png is successfully split into single lines
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Lower threshold in extract_lines_from_images_batch to 1.25 * target_height.
2. Update split_merged_crop_by_projection to use a local minima/valley search in row_sums when simple thresholding doesn't yield multi-line splits.
3. Verify that col_0_line_4.png is cleanly split on seq-3.jp2 and that nearby lines are isolated.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully lowered the line split triggering ratio threshold in extract_lines_from_images_batch from 1.5x to 1.25x target_height (38px). Enhanced split_merged_crop_by_projection to identify local energy/density minima valleys in smoothed row projection profiles when clean whitespace is unavailable. Verified on seq-3.jp2 that 'Civilization is rapidly taken place among' (col_0_line_14.png) is now cleanly isolated from its neighbors ('move off...' and 'them, and...').
<!-- SECTION:FINAL_SUMMARY:END -->

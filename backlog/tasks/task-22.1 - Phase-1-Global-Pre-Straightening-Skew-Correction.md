---
id: TASK-22.1
title: 'Phase 1: Global Pre-Straightening Skew Correction'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-19 14:56'
updated_date: '2026-07-05 20:58'
labels: []
dependencies: []
parent_task_id: TASK-22
ordinal: 143000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Detect and correct skew on the entire page/scan *before* running Surya layout detection to ensure aligned bounding boxes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement page-level skew detection in the layout analysis workflow
- [x] #2 Apply skew correction to the full scan before extraction
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented global pre-straightening skew correction in layout analysis. By calling detect_and_fix_skew on input images before passing them to the layout predictor in extract_columns_batch, we ensure the entire image is straight, aligning columns vertically/horizontally before bboxes are detected.
<!-- SECTION:FINAL_SUMMARY:END -->

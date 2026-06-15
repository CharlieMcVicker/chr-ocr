---
id: TASK-20
title: Fix Column Drift via Global Page Skew Correction
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 20:26'
updated_date: '2026-06-10 20:36'
labels: []
dependencies: []
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Explore strategies to fix non-linear column drift (warping) that isn't solved by global skew correction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Update extract_columns to apply detect_and_fix_skew to the full page
- [ ] #2 Return skew-corrected full page image alongside column data
- [ ] #3 Update extract_lines.py and prepare_training_data.py to crop from the straightened image without redundant skew correction
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Run Surya DetectionPredictor on the full, uncropped page image to find all lines.\n2. Run layout detection to find column bounding boxes.\n3. Calculate the centroid (x, y) for each detected line.\n4. Map each line to a column if its centroid falls within the column's horizontal range.\n5. Crop lines directly from the original image using their specific, tight bounding boxes.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Approaches like global page skew correction and full-page centroid matching failed due to severe non-linear document warping and horizontal column merging. Closing this ticket to track the new approach in a separate ticket.
<!-- SECTION:FINAL_SUMMARY:END -->

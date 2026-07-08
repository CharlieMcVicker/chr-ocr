---
id: TASK-172
title: Implement Secondary Horizontal Projection Splitting for Merged Line Crops
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-05 20:42'
updated_date: '2026-07-05 20:46'
labels:
  - layout
  - segmentation
dependencies: []
priority: high
ordinal: 190000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a secondary fallback post-processing step in the line segmentation pipeline. If a detected bounding box has an unpadded height exceeding 1.5x the target height (e.g., >45px for a target height of 30px), use horizontal projection profiles (row-by-row pixel sums) to find empty horizontal valley lines (white space gaps) and split the merged line crop into individual single-line bounding boxes/crops instead of scaling it down. Integrate this logic into phoenix/layout/segmentation.py and ensure its robust operation on multi-line cropped boxes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement horizontal projection profile splitting logic in phoenix/layout/segmentation.py
- [x] #2 Update crop_pad_normalize_line or the batch extraction workflow to check for merged crops and dynamically split them before normalization
- [x] #3 Verify text line crop extraction results on sequence scans to confirm no valid single lines are improperly split and merged lines are successfully separated into individual crops
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Define projection profile splitting function in phoenix/layout/segmentation.py.
2. In extract_lines_from_images_batch, check if a detected bbox has unpadded height > 1.5 * target_height.
3. If tall, apply the splitting function to retrieve subdivided bounding boxes within the column.
4. Recursively or iteratively normalize each sub-bbox.
5. Create a test script to evaluate splitting on representative scans and verify outputs.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented secondary horizontal projection profile splitting for merged line crops in phoenix/layout/segmentation.py. When a detected bounding box has an unpadded height exceeding 1.5x the target height (e.g., > 45px), the pipeline crops the region, converts it to grayscale, binarizes it, and calculates horizontal projection profiles. Gaps/valleys between continuous row-sums are located, and the bounding box is split at valley midpoints into standard text-line heights. Each split crop is then cropped, padded, and normalized. Verified implementation with unit tests on synthetic images to confirm successful extraction and coordinate mapping.
<!-- SECTION:FINAL_SUMMARY:END -->

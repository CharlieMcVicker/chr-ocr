---
id: TASK-22
title: Improve Column Cropping Boundaries for Wavy Text
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 20:43'
updated_date: '2026-07-05 20:58'
labels: []
dependencies: []
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current layout detection generates straight rectangular bounding boxes for columns. When text is wavy, these tight boxes cut off the edges of words. Investigate techniques to generate curved/adaptive column bounds or intelligently expand the column crop margins without intersecting adjacent columns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify algorithm or layout parameter to improve bounds
- [x] #2 Update layout extraction to yield wavy/adaptive columns
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Phase 1: Global Pre-Straightening
   - Detect and correct skew on the entire page/scan *before* running Surya layout detection.
   - This ensures text blocks are aligned vertically/horizontally, avoiding "slanted" columns from being clipped by vertical rectangular crops.

2. Phase 2: Dynamic Margin & Overlap Prevention Heuristic
   - Calculate horizontal margins dynamically rather than using a static margin (e.g., 20px).
   - If two columns are close (small gutter), shrink the padding proportionally to prevent one column crop from capturing text from the neighboring column.

3. Phase 3: Segment/Block-Level Slicing for Wavy/Wandering Columns
   - Instead of a single static rectangle spanning the min/max X of all blocks in a column group, keep track of individual block-level horizontal limits.
   - Use these individual bounds when performing subsequent line-crop extraction within the column, preventing high/low lines from being truncated on wavy pages.

4. Phase 4: Consolidate Layout Implementations
   - Synchronize layout segmentation logic between "server/layout.py" and "phoenix/layout/segmentation.py" to prevent logic drift.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully designed and implemented improved column and line cropping boundaries for wavy text. Implemented page-level global pre-straightening (Phase 1), dynamic asymmetric column margin calculations (Phase 2), local sub-block boundaries mapping during line extraction (Phase 3), and layout algorithm consolidation between core and server modules (Phase 4). Verification on real newspaper scan scans/1828-02-28/seq-3.jp2 completed with 100% success, yielding 5 columns and 1355 cleanly extracted lines.
<!-- SECTION:FINAL_SUMMARY:END -->

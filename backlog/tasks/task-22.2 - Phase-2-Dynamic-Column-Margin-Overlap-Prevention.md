---
id: TASK-22.2
title: 'Phase 2: Dynamic Column Margin & Overlap Prevention'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-19 14:56'
updated_date: '2026-07-05 20:58'
labels: []
dependencies: []
parent_task_id: TASK-22
ordinal: 144000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Calculate horizontal margins dynamically rather than using a static margin (e.g., 20px) to prevent adjacent columns from overlapping or bleeding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement distance-based padding reduction heuristic for adjacent columns
- [x] #2 Verify that column crops do not intersect with neighboring text blocks
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented compute_dynamic_asymmetric_margins to calculate custom horizontal margins (left and right) for each column. If two columns are very close horizontally, margins are shrunk proportionally (clamped to at most half of the gutter distance), mathematically guaranteeing that columns and adjacent crops do not overlap or intersect.
<!-- SECTION:FINAL_SUMMARY:END -->

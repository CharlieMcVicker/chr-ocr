---
id: TASK-22.3
title: 'Phase 3: Segment-Level Sub-Block Slicing for Columns'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-19 14:56'
updated_date: '2026-07-05 20:58'
labels: []
dependencies: []
parent_task_id: TASK-22
ordinal: 145000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Instead of a single static rectangle spanning the min/max X of all blocks in a column group, keep track of individual block-level horizontal limits during line-crop extraction.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Store individual text block horizontal bounds inside column metadata
- [x] #2 Use block-level local bounds to crop lines, preventing wavy column boundary truncations
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Stored sub-block lists inside column metadata objects. During line extraction, find_best_block determines the local text block that vertically matches each line, then crops the line using these local horizontal bounds from the full straightened page, completely preventing wavy text truncation at column edges.
<!-- SECTION:FINAL_SUMMARY:END -->

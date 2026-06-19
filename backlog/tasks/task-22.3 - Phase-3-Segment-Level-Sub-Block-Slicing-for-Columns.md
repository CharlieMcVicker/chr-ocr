---
id: TASK-22.3
title: 'Phase 3: Segment-Level Sub-Block Slicing for Columns'
status: To Do
assignee: []
created_date: '2026-06-19 14:56'
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
- [ ] #1 Store individual text block horizontal bounds inside column metadata
- [ ] #2 Use block-level local bounds to crop lines, preventing wavy column boundary truncations
<!-- AC:END -->

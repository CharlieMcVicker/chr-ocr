---
id: TASK-19.3
title: 'Phase 3: Line Cropping & Normalization Logic'
status: To Do
assignee: []
created_date: '2026-06-10 20:14'
updated_date: '2026-06-10 20:15'
labels: []
dependencies: []
parent_task_id: TASK-19
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract shared normalization function to server/line_utils.py (Resolves Task 2 as well).
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create `server/line_utils.py`.\n2. Implement `crop_pad_normalize_line(col_crop, bbox, padding_x, padding_y, target_height_range=(30, 33))`.\n3. Logic: Add padding to bbox, crop line from column, measure height. If height < 30 or height <= 1.5 * target_height, keep size. Else, scale down using Lanczos.\n4. Refactor `scripts/prepare_training_data.py` and `scripts/extract_lines.py` to import and call this shared function.
<!-- SECTION:PLAN:END -->

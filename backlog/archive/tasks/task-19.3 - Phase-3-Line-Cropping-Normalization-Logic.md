---
id: TASK-19.3
title: 'Phase 3: Line Cropping & Normalization Logic'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 20:14'
updated_date: '2026-06-10 20:51'
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
1. Extract shared normalization function to server/line_utils.py.\n2. Implement crop_pad_normalize_line(image, bbox, padding_x, padding_y, target_height_range=(30, 33)).\n3. Logic: Measure unpadded bbox height. If scaling is needed (height > 1.5 * target_height), calculate ratio = target_height / unpadded_height. Calculate dynamic_pad = int(padding / ratio). Crop with dynamic padding, then scale by ratio. If no scaling needed, just use standard padding.\n4. Refactor pipeline scripts to use this function.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Extracted line cropping and normalization logic into server/line_utils.py using Option A resizing logic (calculating dynamic padding to preserve requested margins after downscaling). Updated prepare_training_data.py and extract_lines.py to use this utility.
<!-- SECTION:FINAL_SUMMARY:END -->

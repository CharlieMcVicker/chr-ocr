---
id: TASK-124
title: Implement Custom Page Curl and Spine Curvature Distortion
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-06-19 13:14'
updated_date: '2026-06-19 14:18'
labels: []
dependencies: []
modified_files:
  - backlog/docs/research/mixed-training-augmentation.md
ordinal: 138000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Develop a custom coordinate-mapping distortion in phoenix/training/augment.py that simulates the page-curl and cylindrical vertical compression/bending artifacts typical of book spines or bent scan edges.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement a custom OpenCV coordinate-mapping utility in phoenix/training/augment.py that vertically curves and horizontally squishes lines near the left or right image margins.
- [x] #2 Integrate this page-curl transform into the dynamic augmentation pipeline (get_albumentations_pipeline or augment_dynamic.py).
- [x] #3 Expose page-curl probability, direction (left/right/random), and bending/compression intensity factors in the configuration JSON.
- [x] #4 Verify that output line crops visually match the book spine edge curve and squishing artifacts.
- [x] #5 Update the mathematical specification and implementation description of Page Curl and Spine Curvature Distortion in backlog/docs/research/mixed-training-augmentation.md
<!-- AC:END -->









## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement apply_page_curl in phoenix/training/augment.py with vertical bending and horizontal squishing.
2. Create custom Albumentations transform PageCurl and integrate into get_albumentations_pipeline.
3. Support configuring page curl probability, direction, and intensity in configuration.
4. Verify visual output.
5. Update mixed-training-augmentation.md documentation.
<!-- SECTION:PLAN:END -->

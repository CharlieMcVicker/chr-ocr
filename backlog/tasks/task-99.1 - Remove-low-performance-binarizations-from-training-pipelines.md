---
id: TASK-99.1
title: Remove low-performance binarizations from training pipelines
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 02:43'
updated_date: '2026-06-18 02:44'
labels: []
dependencies: []
parent_task_id: TASK-99
ordinal: 109000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove su binarization and sauvola with k >= 0.2 from scripts/augment_dataset.py and scripts/augment_dynamic.py based on sweep evaluation results.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove su binarization and sauvola with k >= 0.2 from scripts/augment_dataset.py
- [x] #2 Remove su binarization and sauvola with k >= 0.2 from scripts/augment_dynamic.py
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed su binarization entirely and Sauvola binarization with k >= 0.2 from both the offline dataset augmentation script (scripts/augment_dataset.py) and the dynamic dataset augmentation script (scripts/augment_dynamic.py). Verified script compilation. All acceptance criteria checked.
<!-- SECTION:FINAL_SUMMARY:END -->

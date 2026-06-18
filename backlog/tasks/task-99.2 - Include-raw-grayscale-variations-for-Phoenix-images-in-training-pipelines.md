---
id: TASK-99.2
title: Include raw grayscale variations for Phoenix images in training pipelines
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-18 02:43'
updated_date: '2026-06-18 02:45'
labels: []
dependencies: []
parent_task_id: TASK-99
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add support for training on raw non-binarized grayscale images for the Cherokee Phoenix dataset to align training data with the optimal evaluation format and improve model accuracy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Include 'grayscale' (native/unbinarized) as a training variation in scripts/augment_dataset.py for Phoenix scans
- [x] #2 Add 'grayscale' (native/unbinarized) to the dynamic binarization selection pool in scripts/augment_dynamic.py for Phoenix scans
- [x] #3 Verify that both static and dynamic training data generation scripts produce grayscale variations alongside binarized ones
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully included grayscale variations in augment_dataset.py and augment_dynamic.py, and verified both scripts generate raw grayscale variations alongside binarized outputs.
<!-- SECTION:FINAL_SUMMARY:END -->

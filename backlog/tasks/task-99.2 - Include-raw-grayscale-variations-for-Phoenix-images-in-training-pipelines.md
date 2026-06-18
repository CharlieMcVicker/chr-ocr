---
id: TASK-99.2
title: Include raw grayscale variations for Phoenix images in training pipelines
status: To Do
assignee: []
created_date: '2026-06-18 02:43'
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
- [ ] #1 Include 'grayscale' (native/unbinarized) as a training variation in scripts/augment_dataset.py for Phoenix scans
- [ ] #2 Add 'grayscale' (native/unbinarized) to the dynamic binarization selection pool in scripts/augment_dynamic.py for Phoenix scans
- [ ] #3 Verify that both static and dynamic training data generation scripts produce grayscale variations alongside binarized ones
<!-- AC:END -->

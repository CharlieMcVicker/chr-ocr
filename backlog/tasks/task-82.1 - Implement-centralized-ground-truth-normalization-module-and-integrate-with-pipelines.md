---
id: TASK-82.1
title: >-
  Implement centralized ground-truth normalization module and integrate with
  pipelines
status: To Do
assignee: []
created_date: '2026-06-18 02:52'
labels: []
dependencies: []
parent_task_id: TASK-82
ordinal: 112000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a centralized normalization module under phoenix/text/normalization.py to handle Unicode NFC normalization, Cherokee character uppercasing, and whitespace normalization, and integrate it with augment_dataset.py, augment_dynamic.py, and evaluation scripts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create phoenix/text/normalization.py with normalize_truth function
- [ ] #2 Integrate normalization into augment_dataset.py and augment_dynamic.py when writing .gt.txt and .box files
- [ ] #3 Integrate normalization into generate_binarization_graphs.py, generate_performance_graphs.py, and evaluate_mixed_model.py comparison logic
<!-- AC:END -->

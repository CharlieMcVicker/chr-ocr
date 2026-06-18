---
id: TASK-82.1
title: >-
  Implement centralized ground-truth normalization module and integrate with
  pipelines
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 02:52'
updated_date: '2026-06-18 12:35'
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
- [x] #1 Create phoenix/text/normalization.py with normalize_truth function
- [x] #2 Integrate normalization into augment_dataset.py and augment_dynamic.py when writing .gt.txt and .box files
- [x] #3 Integrate normalization into generate_binarization_graphs.py, generate_performance_graphs.py, and evaluate_mixed_model.py comparison logic
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented centralized Cherokee ground-truth text normalization (NFC, case folding/uppercasing, and whitespace normalization) under phoenix/text/normalization.py. Fully integrated it across scripts/augment_dataset.py, scripts/augment_dynamic.py, scripts/evaluate_mixed_model.py, scripts/generate_binarization_graphs.py, and scripts/generate_performance_graphs.py. Standardized mix_datasets.py to stably sample CNT lines with '4', brackets, and dynamically test with lowercased Cherokee to confirm full end-to-end normalization correctness.
<!-- SECTION:FINAL_SUMMARY:END -->

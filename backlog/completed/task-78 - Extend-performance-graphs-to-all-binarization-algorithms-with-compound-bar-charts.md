---
id: TASK-78
title: >-
  Extend performance graphs to all binarization algorithms with compound bar
  charts
status: Done
assignee:
  - '@myself'
created_date: '2026-06-16 22:01'
updated_date: '2026-06-17 02:51'
labels: []
dependencies: []
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current generate_performance_graphs.py only evaluates the 'base' (clean grayscale) test split. We need to extend it to evaluate all 30 binarization algorithm subdirectories under training_data/dataset/test/ and produce compound bar charts that show per-file performance broken down by binarization algorithm, so we can understand which source documents and which binarization approaches are hardest for the model.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Script accepts a --test-root argument pointing to the test directory containing all binarization subdirs (default: training_data/dataset/test)
- [x] #2 Script iterates over every binarization algorithm subdirectory and runs lstmeval once per algo (single model load per algo)
- [x] #3 Per-binarization summary bar chart is generated: one bar per algo showing mean CER across all files for that algo, sorted by error rate
- [x] #4 Compound per-file bar chart is generated: major groups are individual source document lines, minor bars within each group represent each binarization algorithm, making it easy to see which files and algos are hardest
- [x] #5 All outputs (charts + markdown report) are saved to training_data/performance_analysis/ with clear filenames
- [x] #6 Encoding errors are handled per the existing approach (CER=100% for skipped lines)
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully developed and ran generate_binarization_graphs.py script to evaluate all 30 binarization algorithms, generating summary and compound plots, as well as a markdown comparative performance report.
<!-- SECTION:FINAL_SUMMARY:END -->

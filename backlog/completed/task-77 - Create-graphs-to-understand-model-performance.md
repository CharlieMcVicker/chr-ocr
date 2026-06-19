---
id: TASK-77
title: Create graphs to understand model performance
status: Done
assignee:
  - '@myself'
created_date: '2026-06-16 21:18'
updated_date: '2026-06-16 21:59'
labels:
  - needs-scoping
dependencies: []
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Histogram of loss by line, barchart by document
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created scripts/generate_performance_graphs.py — runs lstmeval once on the full test set, reads all .gt.txt files from disk for truth matching, handles encoding errors by assigning CER=100%, and produces a histogram of CER by line and a bar chart of mean CER by document page saved to training_data/performance_analysis/.
<!-- SECTION:FINAL_SUMMARY:END -->

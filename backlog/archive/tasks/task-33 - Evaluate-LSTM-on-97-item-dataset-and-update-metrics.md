---
id: TASK-33
title: Evaluate LSTM on 97-item dataset and update metrics
status: Done
assignee: []
created_date: '2026-06-11 14:59'
updated_date: '2026-06-11 15:03'
labels: []
dependencies: []
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
1. Update dataset generation to split using every nth item for perfect distribution across documents. 2. Run the dataset generation and evaluation. 3. Update Model Training Metrics Tracker.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated dataset split to stratified 'every nth' method and evaluated new 97 item dataset. Test accuracy drastically improved from 41.4% to 33.1%, and Sauvola beat Base.
<!-- SECTION:FINAL_SUMMARY:END -->

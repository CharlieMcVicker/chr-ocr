---
id: TASK-156
title: Evaluate CNT-Only Model against Combined Test Set
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-22 19:47'
updated_date: '2026-06-22 19:51'
labels: []
dependencies: []
ordinal: 177000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate the performance of the model trained only on Cherokee New Testament (CNT) synthetic data against the combined evaluation datasets.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Locate the CNT-only model checkpoint
- [x] #2 Execute evaluation script against combined test dataset
- [x] #3 Document and report findings
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully evaluated the CNT-only model checkpoint against the combined evaluation datasets. The model (checkpoint chr_8.773_1463_2250 / cnt_foundation.checkpoint) achieved a Phoenix CER of 15.23% (WER: 49.34%) and a CNT CER of 3.18% (WER: 9.36%), resulting in a Weighted CER of 4.00% (WER: 12.11%). This highlights the necessity of the Phoenix-specific fine-tuning stage to bridge the adaptation gap.
<!-- SECTION:FINAL_SUMMARY:END -->

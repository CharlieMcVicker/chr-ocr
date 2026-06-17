---
id: TASK-83.5
title: View lowest confidence and highest discrepancy OCR reads for New Testament
status: To Do
assignee: []
created_date: '2026-06-17 13:18'
labels:
  - cnt-ocr
dependencies:
  - TASK-83.3
parent_task_id: TASK-83
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Analyze and visualize the lowest confidence and highest discrepancy OCR predictions against the aligned New Testament ground truth. This helps identify systematic OCR failure modes, alignment errors, and potential transcription/ground truth issues.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Run FTM/OCR model on the aligned New Testament line crops and generate predictions with confidence scores
- [ ] #2 Rank results by lowest confidence and highest character-level discrepancy (edit distance/CER) compared to aligned ground truth
- [ ] #3 Output a report or visualization showing the worst-performing OCR reads to facilitate error analysis
<!-- AC:END -->

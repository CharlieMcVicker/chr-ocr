---
id: TASK-55
title: Use confidence readings to do CHR/ENG line classification
status: To Do
assignee: []
created_date: '2026-06-15 18:05'
updated_date: '2026-06-15 19:53'
labels: []
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use the confidence readings from Tesseract's eng and chr models, combined with the latest Fine-Tuned Model (FTM) confidence ratings, to classify the language of line crops. We will perform parameter search to identify optimal weights and threshold values for this scoring/classification heuristic.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement a line scoring function combining eng, chr, and FTM confidence values
- [ ] #2 Execute parameter search to find optimal scoring weights and threshold settings
- [ ] #3 Validate line classification accuracy on a set of labeled test line crops
- [ ] #4 Integrate the classification utility into the training data preparation or labeling pipeline
<!-- AC:END -->

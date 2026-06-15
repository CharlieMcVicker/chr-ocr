---
id: TASK-23
title: Investigate Line-By-Line Language Classification
status: To Do
assignee:
  - '@antigravity'
created_date: '2026-06-10 21:01'
updated_date: '2026-06-15 19:53'
labels:
  - research
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate Cherokee vs Latin language line-by-line rather than column-by-column, focusing on Mixed columns. Compare results/token counts from Tesseract using chr+eng, chr, and eng models. Identify if we can avoid writing purely English line images to disk to avoid manual sorting during labeling. We can augment our false positives for Cherokee using all the 'not Cherokee' labels from the labeling UX.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Spike completed but results were rough on dirty images. See doc-6 for full report. Paused for now.
<!-- SECTION:NOTES:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Develop or run a comparison script across a test dataset containing known Cherokee, English, and Mixed lines
- [ ] #2 Augment Cherokee false positives using 'not Cherokee' labels extracted from the labeling UX
- [ ] #3 Measure false-positive and false-negative rates for the chr, eng, and chr+eng models under different binarization/preprocessing configs
- [ ] #4 Document findings and final recommendation in a research doc under backlog/docs/research/
<!-- AC:END -->

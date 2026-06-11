---
id: TASK-23
title: Investigate Line-By-Line Language Classification
status: To Do
assignee:
  - '@antigravity'
created_date: '2026-06-10 21:01'
updated_date: '2026-06-11 00:01'
labels:
  - research
  - needs-scoping
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Should we estimate Cherokee vs Latin language line-by-line rather than column-by-column? Currently, 'Mixed' columns are rough.\n\nIdeas:\n- Compare results/token counts from Tesseract using `chr+eng`, `chr`, and `eng` models to determine true language.\n- Goal: Avoid writing purely English line images to disk so they don't have to be manually sorted during labeling.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Spike completed but results were rough on dirty images. See doc-6 for full report. Paused for now.
<!-- SECTION:NOTES:END -->

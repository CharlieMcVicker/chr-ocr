---
id: TASK-83.6
title: Flag incongruous lines in CNT using Bible Gateway reference data
status: To Do
assignee: []
created_date: '2026-06-17 13:18'
labels:
  - cnt-ocr
dependencies:
  - TASK-83.1
parent_task_id: TASK-83
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Cross-reference the Cherokee New Testament (CNT) digital text scraped from cherokeedictionary.net against Cherokee Bible text from Bible Gateway (which typically contains fewer transcription errors). Identify lines/verses that differ between the two sources to flag them for human reconciliation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Scrape or acquire the corresponding Cherokee Bible text from Bible Gateway
- [ ] #2 Write a script to align and compare the two text sources verse-by-verse / line-by-line
- [ ] #3 Generate a report of mismatching lines to flag them for human reconciliation
<!-- AC:END -->

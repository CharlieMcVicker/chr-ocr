---
id: TASK-113
title: Create labeling interface for low confidence columns
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 20:08'
updated_date: '2026-06-18 20:13'
labels: []
dependencies: []
ordinal: 127000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Design and implement a labeling workflow inside the web interface to display and label whole low-confidence text columns (e.g., mean confidence < 75%), enabling users to transcribe or correct full column blocks consecutively.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify low-confidence columns based on mean line confidence scores
- [x] #2 Create a backend route/API to fetch low-confidence column data and images
- [x] #3 Implement a frontend layout displaying the whole column crop with individual line transcribing inputs
- [x] #4 Provide save/skip actions to persist corrections back to the manifest
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Designed and implemented a low-confidence column-level labeling workflow inside the web interface. This includes calculating column mean confidence scores from individual line crops, serving grouped column details via new backend endpoints (/training/columns, /training/columns/save), and displaying a premium dark-themed visual stack layout with interactive text-input cards, keyboard navigation, and bulk-save actions.
<!-- SECTION:FINAL_SUMMARY:END -->

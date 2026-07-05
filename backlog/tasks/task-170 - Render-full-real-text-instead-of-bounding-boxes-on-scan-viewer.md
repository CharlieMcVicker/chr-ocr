---
id: TASK-170
title: Render full real text instead of bounding boxes on scan viewer
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-05 20:29'
updated_date: '2026-07-05 20:30'
labels: []
dependencies: []
priority: high
ordinal: 191000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
On the left scan viewer, display the full real text of each line instead of truncated text inside bounding boxes. Style the lines without the explicit default dashed borders and background colors so it looks like a real text column, while keeping high-fidelity highlight/hover states.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Remove truncated slice and render full line text
- [x] #2 Remove default dashed borders and background color from bbox so it renders as clean text
- [x] #3 Retain visual hover, search match, and active search match highlights around/under the text lines
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Modified the left side scan viewer in the frontend to display the full real text of each line instead of truncated text inside bounding boxes. Style updates were made in App.tsx and App.css to hide bounding box borders and background styling by default, resulting in a clean document column visualization while maintaining hover and search highlights.
<!-- SECTION:FINAL_SUMMARY:END -->

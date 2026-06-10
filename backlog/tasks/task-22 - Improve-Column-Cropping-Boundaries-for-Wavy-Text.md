---
id: TASK-22
title: Improve Column Cropping Boundaries for Wavy Text
status: To Do
assignee: []
created_date: '2026-06-10 20:43'
labels: []
dependencies: []
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The current layout detection generates straight rectangular bounding boxes for columns. When text is wavy, these tight boxes cut off the edges of words. Investigate techniques to generate curved/adaptive column bounds or intelligently expand the column crop margins without intersecting adjacent columns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Identify algorithm or layout parameter to improve bounds
- [ ] #2 Update layout extraction to yield wavy/adaptive columns
<!-- AC:END -->

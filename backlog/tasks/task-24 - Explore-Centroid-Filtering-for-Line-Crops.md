---
id: TASK-24
title: Explore Centroid Filtering for Line Crops
status: To Do
assignee: []
created_date: '2026-06-10 21:01'
labels:
  - idea
  - needs-scoping
dependencies: []
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Idea: Use centroid math to drop small fragments of neighboring lines from other columns that accidentally get picked up during cropping. If a line's centroid is far outside the main column distribution, it's likely a fragment and can be dropped.
<!-- SECTION:DESCRIPTION:END -->

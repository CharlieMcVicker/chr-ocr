---
id: TASK-24
title: Explore Centroid Filtering for Line Crops
status: To Do
assignee: []
created_date: '2026-06-10 21:01'
updated_date: '2026-06-15 19:53'
labels:
  - idea
dependencies: []
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use centroid math to drop small fragments of neighboring lines from other columns that accidentally get picked up during cropping. If a line's centroid is far outside the main column distribution, it's likely a fragment and can be dropped.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Calculate the distribution of horizontal centroids for lines within each column
- [ ] #2 Implement an outlier detection filter (e.g. standard deviation or bounds check) to drop line crops that fall outside the column's horizontal span
- [ ] #3 Integrate centroid-based filtering into the data preparation workflow and verify no valid lines are dropped on test scans
<!-- AC:END -->

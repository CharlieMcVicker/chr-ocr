---
id: TASK-13
title: Diagnose column bbox combining
status: Done
assignee: []
created_date: '2026-06-10 19:17'
updated_date: '2026-06-10 19:19'
labels: []
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create an auxiliary script to scatter plot bboxes and diagnose why we generate 15+ columns instead of the expected ~4 for some scans.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Find a scan with 15+ columns
- [x] #2 Create a python script to scatter plot bboxes
- [x] #3 Diagnose column combining logic
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created diagnose_columns.py and used ./scans/1828-02-21/seq-1.jp2 (which produced 22 columns) to generate a scatter plot.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created scripts/diagnose_columns.py to scatter plot the bounding boxes to diagnose grouping logic. Ran it successfully on scans/1828-02-21/seq-1.jp2. Also created a backlog doc to clarify the usage of uploads/manifest.json.
<!-- SECTION:FINAL_SUMMARY:END -->

---
id: TASK-83.2
title: Extract line images from Cherokee New Testament scans
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 12:55'
updated_date: '2026-06-17 13:10'
labels:
  - cnt-ocr
dependencies: []
parent_task_id: TASK-83
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Perform line extraction/segmentation on the downloaded verse images.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement line segmenter/cropper for New Testament verse scans
- [x] #2 Store segmented line crops in organized output folders
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Batch segmented verse scans for Book 01 Matthew Chapter 1 and saved segment_map.json
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully implemented segment_verses.py to load, segment, and crop Cherokee NT verse scans using Surya, producing crops for 25 verses and recording the segment map in segment_map.json.
<!-- SECTION:FINAL_SUMMARY:END -->

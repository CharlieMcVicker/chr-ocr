---
id: TASK-91
title: Update stale references to training_data_v2 in OCR Operations Guide
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 19:07'
updated_date: '2026-06-17 19:09'
labels: []
dependencies: []
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Cherokee OCR Operations Guide (doc-13) references the path 'training_data_v2/' throughout its steps. However, the active manifest, line crops, and dataset folders on disk are located under 'training_data/'. Update the documentation to correct these references and keep it synchronized with the actual filesystem structure.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace all instances of 'training_data_v2/' with 'training_data/' in doc-13
- [x] #2 Verify other paths and script references in doc-13 match the active repo structure
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Merged spike-scrape-cherokee-testament onto main and replaced all stale 'training_data_v2/' paths with 'training_data/' in the OCR Operations Guide (doc-13).
<!-- SECTION:FINAL_SUMMARY:END -->

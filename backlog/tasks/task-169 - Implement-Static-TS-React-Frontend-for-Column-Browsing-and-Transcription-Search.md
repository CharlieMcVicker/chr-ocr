---
id: TASK-169
title: >-
  Implement Static TS/React Frontend for Column Browsing and Transcription
  Search
status: Done
assignee:
  - '@myself'
created_date: '2026-07-05 20:20'
updated_date: '2026-07-05 20:25'
labels: []
dependencies: []
priority: high
ordinal: 190000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a static TypeScript/React frontend deployed to GitHub Pages that runs offline search and column browsing. It features a two-column view (scanned column with line bboxes on the left, transcription lines on the right), bidirectional hover highlighting, and query-based search with Next/Back navigation across lines and columns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Initialize a TS/React application using Vite in the 'frontend' directory
- [x] #2 Implement the layout with scanned column with bounding boxes on the left, and transcription list on the right
- [x] #3 Sync hover highlighting between bounding boxes on the left and transcription lines on the right
- [x] #4 Implement offline search bar on the right that matches queries against column transcriptions
- [x] #5 Implement 'Next/Back' navigation buttons that step through matching search results, transitioning to the next column when no more results exist in the current one
- [x] #6 Support loading and serving transcription and bbox data from a local JSON index file
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented a highly interactive, responsive TS/React browser application for column scan visualization and transcription search under 'frontend'. Created a script 'scripts/build_frontend_index.py' to generate a public search index 'frontend/public/ocr_data.json' from 'manifest.json' (producing 53 columns with precise line-by-line bounding boxes). Implemented bidirectionally synced hover highlighting, query-based search supporting Cherokee unicode, and Next/Back search results navigation across columns. Designed with a clean, high-contrast, minimalist monochrome light layout.
<!-- SECTION:FINAL_SUMMARY:END -->

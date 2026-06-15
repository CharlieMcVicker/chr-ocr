---
id: TASK-3
title: Implement Cherokee Phoenix Scan Downloader Script
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-10 14:33'
labels: []
dependencies: []
modified_files:
  - scripts/download_scans.py
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a downloader script that parses the scan URLs from a text file, templates sequence numbers, downloads JP2 images, handles 404/HTTP errors as termination signals, and organizes downloads by issue date.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Parse base URLs, date, and edition from a given text file
- [x] #2 Sequentially download scan images (seq-N.jp2) using curl
- [x] #3 Handle out-of-bounds 404 responses to stop download sequences for each issue
- [x] #4 Save files locally organized by issue date inside the scans directory
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Parse foo.txt for URL patterns\n2. Download images using curl\n3. Handle 404 responses\n4. Save files to scans/ directory
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully implemented a recursive scan downloader script in scripts/download_scans.py that parses URLs, downloads scan images, and handles out-of-bounds HTTP 404 responses.
<!-- SECTION:FINAL_SUMMARY:END -->

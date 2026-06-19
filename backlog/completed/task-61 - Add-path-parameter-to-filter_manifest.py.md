---
id: TASK-61
title: Add path parameter to filter_manifest.py
status: Done
assignee:
  - '@myself'
created_date: '2026-06-15 23:57'
updated_date: '2026-06-15 23:58'
labels: []
dependencies: []
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update scripts/filter_manifest.py to accept the manifest path and image directory as command-line parameters instead of hardcoding training_data/manifest.json.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 scripts/filter_manifest.py accepts --manifest and --image-dir command-line arguments
- [x] #2 The script defaults to the original paths for backward compatibility if arguments are not provided
- [x] #3 The script successfully runs and filters the target manifest file
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated scripts/filter_manifest.py to accept --manifest and --image-dir parameters, falling back to 'training_data/manifest.json' and 'training_data' defaults if not provided. Verified that the modified script successfully filters the target manifest file.
<!-- SECTION:FINAL_SUMMARY:END -->

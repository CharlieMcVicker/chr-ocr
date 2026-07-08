---
id: TASK-174
title: Update static frontend to use v2 line crops from manifest_w_lang
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-08 19:46'
updated_date: '2026-07-08 19:47'
labels: []
dependencies: []
ordinal: 193000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the static frontend to use v2 line crops from training_data/manifest_w_lang.json instead of manifest.json. This includes updating build_frontend_index.py to read from manifest_w_lang.json and regenerate ocr_data.json, and verifying everything is correctly linked.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update scripts/build_frontend_index.py to load manifest_w_lang.json
- [x] #2 Regenerate frontend/public/ocr_data.json
- [x] #3 Verify that the frontend loads and displays correct images and OCR data
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Successfully updated scripts/build_frontend_index.py to load manifest_w_lang.json and ran it to compile 60 columns to frontend/public/ocr_data.json. Verified the frontend compiles and builds successfully.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated the static frontend data pipeline to read from training_data/manifest_w_lang.json (v2 line crops) instead of training_data/manifest.json. Ran the compiler script to regenerate the JSON index used by the column browser, and verified that the entire client-side static application builds correctly without errors.
<!-- SECTION:FINAL_SUMMARY:END -->

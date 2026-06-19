---
id: TASK-86
title: Automate ground truth space correction with exclusion list
status: Done
assignee:
  - '@subagent'
created_date: '2026-06-17 13:57'
updated_date: '2026-06-17 14:00'
labels:
  - data
  - ocr
dependencies: []
modified_files:
  - training_data/cnt/book_01/metadata.json
  - training_data/cnt/book_01/segment_map.json
  - training_data/cnt/book_01/aligned_manifest.json
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable automatic correction of detected missing spaces in Cherokee New Testament ground truth. We should apply these splitting decisions by default during alignment, but support a configurable exclusion list or override file to disable any specific splitting decisions that humans review and reject.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement utility to apply space corrections automatically to metadata.json/segment_map.json
- [x] #2 Support an override/exclusion file to disable specific splitting decisions
- [x] #3 Integrate this step seamlessly into the ingestion/alignment pipeline
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create scripts/apply_space_corrections.py to detect space candidates from aligned_manifest.json, filter by space_correction_exclusions.json, and apply corrections to metadata.json and segment_map.json.\n2. Modify scripts/align_verses.py to integrate apply_space_corrections, re-running alignment if any corrections were applied to ensure final alignment is correct.\n3. Create test/verification script or run and verify on book_01.\n4. Commit changes and mark task done.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created scripts/apply_space_corrections.py to automatically apply missing space corrections detected in the aligned manifest. Added support for space_correction_exclusions.json to skip corrections. Integrated the correction utility into scripts/align_verses.py to auto-correct ground truth and re-run alignment if any corrections are made.
<!-- SECTION:FINAL_SUMMARY:END -->

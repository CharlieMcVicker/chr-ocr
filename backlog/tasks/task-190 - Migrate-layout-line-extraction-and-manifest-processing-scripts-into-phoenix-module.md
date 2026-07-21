---
id: TASK-190
title: >-
  Migrate layout, line extraction, and manifest processing scripts into phoenix
  module
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 16:13'
updated_date: '2026-07-21 16:40'
labels: []
dependencies: []
ordinal: 198000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move extract_lines.py, extract_low_confidence_rare_crops.py, classify_layout.py, find_line_class_params.py, align_verses.py, segment_verses.py, add_predicted_lang_to_manifest.py, enrich_manifest_with_ftm.py, filter_manifest.py, build_frontend_index.py, update_unicharsets.py into appropriate phoenix packages.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move layout, manifest, text, and tooling scripts into phoenix packages
- [x] #2 Update callers and commands
- [x] #3 Pass all tests
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Migrated layout, manifest, and text scripts into phoenix subpackages (phoenix/layout, phoenix/manifest, phoenix/text), updated imports and callers, and verified with pytest suite.
<!-- SECTION:FINAL_SUMMARY:END -->

---
id: TASK-19.1
title: 'Phase 1: Environment & File Cleanup'
status: Done
assignee: []
created_date: '2026-06-10 20:14'
updated_date: '2026-06-10 20:16'
labels: []
dependencies: []
parent_task_id: TASK-19
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Delete overlay files, wipe corrupted dataset, and ignore overlays in find_scans.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Delete all `bbox_overlay_*.png` files in the `scans/` directory.\n2. Delete the `training_data_v2/` directory to clear out bad crops.\n3. Update `find_scans()` in `scripts/prepare_training_data.py` to explicitly ignore any file starting with `bbox_overlay_`.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Deleted training_data_v2/ and scans/bbox_overlay_*.png. Updated find_scans() to ignore bbox_overlay_ files.
<!-- SECTION:FINAL_SUMMARY:END -->

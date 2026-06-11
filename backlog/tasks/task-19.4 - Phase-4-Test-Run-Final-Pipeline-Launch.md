---
id: TASK-19.4
title: 'Phase 4: Test Run & Final Pipeline Launch'
status: Done
assignee: []
created_date: '2026-06-10 20:14'
updated_date: '2026-06-11 03:11'
labels: []
dependencies: []
parent_task_id: TASK-19
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run a 5-document test on sticky scans, verify crops, launch full pipeline, and reconsolidate labels.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Run a 5-document test on sticky scans using `python scripts/prepare_training_data.py --limit 5` with scans like 1828-07-02_seq-1, 1828-03-27_seq-3.\n2. Visually verify the crops in `training_data_v2/line_crops`.\n3. Once verified, run the full pipeline without the limit flag in the background.\n4. After completion, run `python scripts/reconsolidate_labels.py` to port existing v1 labels to the new dataset.
<!-- SECTION:PLAN:END -->

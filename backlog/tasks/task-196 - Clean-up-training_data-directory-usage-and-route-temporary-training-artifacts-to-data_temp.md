---
id: TASK-196
title: >-
  Clean up training_data directory usage and route temporary training artifacts
  to data_temp/
status: Done
assignee:
  - '@agent-k'
created_date: '2026-07-21 19:09'
updated_date: '2026-07-21 19:10'
labels: []
dependencies: []
ordinal: 202000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Redirect generated dynamic training data (augmented images, train.list, lstmf outputs, cached datasets) from training_data/ to a separate temp directory (e.g. data_temp/) for periodic cleanup while keeping core dataset files intact in training_data/.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify all generation/output paths in phoenix module and training scripts that produce temporary training artifacts
- [x] #2 Update TrainingConfig and relevant training pipeline components to default output/temp directories to data_temp/
- [x] #3 Update .gitignore and documentation to reflect the new data_temp/ usage
- [x] #4 Verify training scripts run properly with the updated directory routing
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Audit codebase for paths generating temporary training artifacts under training_data/\n2. Update TrainingConfig defaults and references in phoenix module (config.py, augment_dynamic.py, sweep.py, train_staged.py, etc.) to use data_temp/\n3. Update .gitignore to ignore data_temp/\n4. Run python/pytest checks to verify directory creation and training workflow integration
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Re-routed generated dynamic training paths (intermediate epoch dataset directories, staged training outputs, master pools, train.list generation, and CNT sample caches) from training_data/ to data_temp/. Updated TrainingConfig defaults, train.py, sweep.py, pre_augment_cnt.py, and .gitignore to ensure training_data/ retains core datasets while data_temp/ safely holds temporary outputs for periodic cleanup.
<!-- SECTION:FINAL_SUMMARY:END -->

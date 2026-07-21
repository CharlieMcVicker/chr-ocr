---
id: TASK-199
title: >-
  Clean up TrainingConfig JSON serialization and remove null fields from
  cnt-pretrain.json
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 21:29'
updated_date: '2026-07-21 21:29'
labels: []
dependencies: []
ordinal: 205000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update TrainingConfig.to_dict() to filter out internal private fields starting with '_' and null/None values, and regenerate configs/cnt-pretrain/cnt-pretrain.json.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update TrainingConfig.to_dict() in phoenix/config.py to omit None values and internal private fields
- [x] #2 Regenerate configs/cnt-pretrain/cnt-pretrain.json without null fields
- [x] #3 Verify python tests and config loading
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update TrainingConfig.to_dict() in phoenix/config.py to strip private internal fields starting with '_' and None/null values.
2. Re-save configs/cnt-pretrain/cnt-pretrain.json.
3. Validate loading configs with pytest / python script.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated TrainingConfig.to_dict() in phoenix/config.py to strip private internal fields and None/null values during serialization. Re-saved configs/cnt-pretrain/cnt-pretrain.json cleanly without null fields.
<!-- SECTION:FINAL_SUMMARY:END -->

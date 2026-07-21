---
id: TASK-188
title: Delete temporary spike and legacy script files
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 16:13'
updated_date: '2026-07-21 16:14'
labels: []
dependencies: []
ordinal: 196000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove obsolete one-off scripts, old shell wrappers, temporary spikes, and legacy migration tools from scripts/ directory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Delete spike_*.py, spike_*.sh, legacy migration scripts, clean-img, call-tesseract, textcleaner
- [x] #2 Ensure remaining scripts and modules are unaffected
- [x] #3 Pass all tests
<!-- AC:END -->

## Summary
Deleted all obsolete spike scripts (`spike_*.py`, `spike_*.sh`), legacy migration files (`recreate_crops.py`, `migrate_v2_crops.py`, `clean_manifest_errors.py`, `update_doc_9.py`, `search_candidates.py`, `reconsolidate_labels.py`, `evaluate_split.sh`, `evaluate_v2.sh`, `prepare_splits.sh`, `split_train_test.py`), `sweep_config.json`, and legacy binary/shell utilities (`clean-img`, `call-tesseract`, `textcleaner`). Verified that unit tests pass cleanly (`PYTHONPATH=. uv run pytest phoenix/`).

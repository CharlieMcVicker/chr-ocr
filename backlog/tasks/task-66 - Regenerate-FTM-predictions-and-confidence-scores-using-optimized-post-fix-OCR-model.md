---
id: TASK-66
title: >-
  Regenerate FTM predictions and confidence scores using optimized post-fix OCR
  model
status: To Do
assignee: []
created_date: '2026-06-16 13:20'
labels: []
dependencies: []
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Now that we have trained a superior post-fix OCR model (average BCER 12.357%), we must regenerate the FTM predictions and character/word confidence scores in the master manifest file (training_data_v2/manifest_w_lang.json) to update the labeling interface with highly accurate predictions and low-confidence sorting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Run FTM prediction enrichment script (enrich_manifest_with_ftm.py) with the new optimal model checkpoint
- [ ] #2 Verify that the master manifest file contains updated predictions and confidence scores
<!-- AC:END -->

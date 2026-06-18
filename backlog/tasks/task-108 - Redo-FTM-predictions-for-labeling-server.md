---
id: TASK-108
title: Redo FTM predictions for labeling server
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 17:43'
updated_date: '2026-06-18 17:51'
labels: []
dependencies: []
ordinal: 122000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Regenerate FTM predictions and confidence scores in manifest_w_lang.json using the latest best OCR model checkpoint (from TASK-106) to improve labeling accuracy and sorting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ensure the best model is copied or compiled as chr_best_finetuned.traineddata
- [x] #2 Run scripts/enrich_manifest_with_ftm.py with --force to recreate predictions on manifest_w_lang.json
- [x] #3 Verify that manifest_w_lang.json has updated ftm_ocr and ftm_confidence values
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully compiled the record-low 3.09% CER model (checkpoint chr_8.025_3272_6100.checkpoint from TASK-106) into chr_best_finetuned.traineddata. Regenerated all 2,959 FTM predictions and word confidence scores on manifest_w_lang.json using the newly compiled best model to improve labeling accuracy and sorting on the labeling server.
<!-- SECTION:FINAL_SUMMARY:END -->

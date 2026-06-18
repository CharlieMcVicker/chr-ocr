---
id: TASK-103
title: >-
  Consolidate unicharset to support both historic NAH character and new
  characters
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 13:08'
updated_date: '2026-06-18 13:20'
labels: []
dependencies: []
ordinal: 117000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Consolidate the Tesseract unicharset files to support the historic NAH character (Ꮐ), the newly added supporting characters ('4', '[', ']'), and the question mark ('?'). Update the base/starter models to contain the combined unicharset, compile the traineddata, and rerun fine-tuning/evaluation to ensure full support for all characters without regressions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rebuild the base chr.traineddata model using combine_tessdata with the consolidated unicharset
- [x] #2 Rerun the fine-tuning script to train a model containing all four characters
- [x] #3 Verify that the compiled model successfully evaluates on both Phoenix and CNT datasets without true encoding errors for these characters
- [x] #4 Add 'Ꮐ' (U+13C0), '4', '[', ']', and '?' to dataset/model/chr.lstm-unicharset and training_data/dataset/model/starter/chr/chr.lstm-unicharset
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Consolidated unicharset files to support Ꮐ (U+13C0), 4, [, ], and ? across target and starter models. Compiled and fine-tuned the model for 20 epochs with a constant 0.0005 LR and 0.4 mixture ratio, which achieved a CER of 7.21% on Phoenix (down from 22.68%) and 3.24% on CNT (down from 14.41%).
<!-- SECTION:FINAL_SUMMARY:END -->

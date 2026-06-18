---
id: TASK-103
title: >-
  Consolidate unicharset to support both historic NAH character and new
  characters
status: To Do
assignee: []
created_date: '2026-06-18 13:08'
labels: []
dependencies: []
ordinal: 117000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Consolidate the Tesseract unicharset files to support both the historic NAH character (Ꮐ) and the newly added supporting characters ('4', '[', ']'). Update the base/starter models to contain the combined unicharset, compile the traineddata, and rerun fine-tuning/evaluation to ensure full support for all characters without regressions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add 'Ꮐ' (U+13C0), '4', '[', and ']' to dataset/model/chr.lstm-unicharset and training_data/dataset/model/starter/chr/chr.lstm-unicharset
- [ ] #2 Rebuild the base chr.traineddata model using combine_tessdata with the consolidated unicharset
- [ ] #3 Rerun the fine-tuning script to train a model containing all four characters
- [ ] #4 Verify that the compiled model successfully evaluates on both Phoenix and CNT datasets without true encoding errors for these characters
<!-- AC:END -->

---
id: TASK-82.2
title: 'Update unicharset files to include ''4'', ''['', and '']'''
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 02:52'
updated_date: '2026-06-18 12:38'
labels: []
dependencies: []
parent_task_id: TASK-82
ordinal: 113000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract and modify Tesseract unicharset files in the repository to include '4', '[', and ']', incrementing character counts and recreating starter/model traineddata files using combine_tessdata.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add '4', '[', and ']' to dataset/model/chr.lstm-unicharset and training_data/dataset/model/starter/chr/chr.lstm-unicharset
- [x] #2 Recreate chr.traineddata in both directories using combine_tessdata -o with the updated unicharsets
- [x] #3 Verify unicharset components contain the new characters using combine_tessdata -u or combine_tessdata -d
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created and executed scripts/update_unicharsets.py to add characters 4, [, and ] to all unicharset files. Rebuilt both target and starter traineddata files using combine_tessdata -o and verified the new sizes and characters are present in the final files.
<!-- SECTION:FINAL_SUMMARY:END -->

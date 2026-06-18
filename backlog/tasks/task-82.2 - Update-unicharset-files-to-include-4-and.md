---
id: TASK-82.2
title: 'Update unicharset files to include ''4'', ''['', and '']'''
status: To Do
assignee: []
created_date: '2026-06-18 02:52'
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
- [ ] #1 Add '4', '[', and ']' to dataset/model/chr.lstm-unicharset and training_data/dataset/model/starter/chr/chr.lstm-unicharset
- [ ] #2 Recreate chr.traineddata in both directories using combine_tessdata -o with the updated unicharsets
- [ ] #3 Verify unicharset components contain the new characters using combine_tessdata -u or combine_tessdata -d
<!-- AC:END -->

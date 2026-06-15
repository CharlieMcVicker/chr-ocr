---
id: TASK-58
title: Dry-Run Line Classification Filtering on Manifest to Identify Dropped Crops
status: To Do
assignee: []
created_date: '2026-06-15 23:21'
labels: []
dependencies: []
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Execute a dry run of the newly integrated confidence-weighted line classification heuristic on the active manifest (manifest_w_lang.json or manifest.json) in training_data_v2. The goal is to generate a comprehensive report of which line crop items would be classified as 'English' or 'Empty' and consequently dropped from the active Cherokee dataset, validating that we do not drop actual Cherokee content.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create a dry-run reporting script that loads the manifest and runs classify_line_image on each unlabeled line crop
- [ ] #2 Generate a report (CSV/JSON/HTML) listing all line crops that would be dropped (classified as English or Empty), including their path, OCR transcriptions, and scores
- [ ] #3 Manually inspect a sample of the dropped lines to confirm they contain zero Cherokee text
- [ ] #4 Verify that no valid Cherokee lines are flagged for dropping, adjusting the classification threshold slightly if any Cherokee false drops are found
<!-- AC:END -->

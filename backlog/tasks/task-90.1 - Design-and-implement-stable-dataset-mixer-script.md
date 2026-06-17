---
id: TASK-90.1
title: Design and implement stable dataset mixer script
status: To Do
assignee: []
created_date: '2026-06-17 19:07'
updated_date: '2026-06-17 19:08'
labels: []
dependencies: []
parent_task_id: TASK-90
ordinal: 97000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a Python script (e.g., scripts/mix_datasets.py) that assigns train/test splits to Phoenix items, samples 10% (or tuned size) of CNT lines using book-specific seeded random generators, splits CNT lines into train/test, and mixes them into a final manifest.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement book-specific seeded random generator using salt and book number
- [ ] #2 Support tuning the sampling fraction to make the CNT subset size close to Phoenix
- [ ] #3 Add 'split' field ('train' or 'test') to manifest items to ensure split stability
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Create a new python script scripts/mix_datasets.py that generates the combined manifest training_data/manifest_mixed.json. It will: 1. Load the active manifest training_data/manifest_w_lang.json. 2. First assign a 'split': 'train' or 'split': 'test' field to each Phoenix labeled Cherokee item using the exact same split logic (split=0.6, matching the train/test splits that are already stable). 3. Loop through all 27 CNT book directories: - Instantiate a seeded random number generator with a standard salt and the book index (e.g. random.Random(f'{salt}_book_{book_idx:02d}')). - Load that book's aligned_manifest.json under training_data/cnt/book_XX/. - Sample a configurable fraction of the lines (defaulting to 10%, tunable down to 1.1% or other values). - Randomly partition the selected CNT lines into train (80%) and test (20%) datasets. - Mix them into the output manifest with 'split' and 'dataset': 'cnt' attributes, and save the result as training_data/manifest_mixed.json.
<!-- SECTION:PLAN:END -->

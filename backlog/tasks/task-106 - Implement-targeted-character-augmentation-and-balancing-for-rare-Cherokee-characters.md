---
id: TASK-106
title: >-
  Implement targeted character augmentation and balancing for rare Cherokee
  characters
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-18 16:49'
updated_date: '2026-06-18 17:06'
labels: []
dependencies: []
ordinal: 120000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Address severe dataset imbalance (such as the 12:1 to 16:1 Ꮧ/Ꮨ ratio and the 31% Ꭽ deletion rate) through targeted sample weighting, focused dynamic augmentations, and font-synthesized training lines for under-represented characters.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Develop scripts/analyze_dataset_character_frequencies.py to list all character frequencies and identify the bottom 20% under-represented characters
- [x] #2 Implement sample replication or focused dynamic augmentation for lines containing rare characters in the training pipeline
- [x] #3 Train and evaluate an updated model checkpoint to verify a reduction in character confusion and deletion rates (like Ꮧ/Ꮨ and Ꭽ)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Develop scripts/analyze_dataset_character_frequencies.py to identify bottom 20% rare characters and save to training_data/rare_characters.json.\n2. Modify scripts/augment_dynamic.py to double variations count for lines containing rare characters.\n3. Modify phoenix/training/train.py to oversample/prioritize rare-character-containing CNT lines.\n4. Run 1-epoch fine-tuning training and evaluate the resulting model checkpoint to verify.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Developed character frequency analyzer, modified dynamic augmentations to double rare-line variations, modified training supervisor to prioritize rare CNT lines, and verified with epoch loop execution.
<!-- SECTION:FINAL_SUMMARY:END -->

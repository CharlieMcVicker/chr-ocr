---
id: TASK-106
title: >-
  Implement targeted character augmentation and balancing for rare Cherokee
  characters
status: To Do
assignee: []
created_date: '2026-06-18 16:49'
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
- [ ] #1 Develop scripts/analyze_dataset_character_frequencies.py to list all character frequencies and identify the bottom 20% under-represented characters
- [ ] #2 Implement sample replication or focused dynamic augmentation for lines containing rare characters in the training pipeline
- [ ] #3 Generate synthetic training lines using multiple Cherokee fonts specifically for the identified rare characters
- [ ] #4 Train and evaluate an updated model checkpoint to verify a reduction in character confusion and deletion rates (like Ꮧ/Ꮨ and Ꭽ)
<!-- AC:END -->

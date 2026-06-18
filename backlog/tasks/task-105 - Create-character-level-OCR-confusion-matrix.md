---
id: TASK-105
title: Create character-level OCR confusion matrix
status: To Do
assignee: []
created_date: '2026-06-18 15:45'
labels: []
dependencies: []
ordinal: 119000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a script to generate a confusion matrix of character-level substitution errors to analyze which Cherokee syllables/characters the fine-tuned model frequently confuses (e.g. Ꮐ vs Ꮑ). This will guide targeted dataset balancing and augmentation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/generate_confusion_matrix.py
- [ ] #2 Load ground truth and OCR predictions on the test set
- [ ] #3 Perform character-level alignment to identify insertions, deletions, and substitutions
- [ ] #4 Generate a formatted confusion matrix (CSV/Markdown) of the top confused character pairs
<!-- AC:END -->

---
id: TASK-105
title: Create character-level OCR confusion matrix
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 15:45'
updated_date: '2026-06-18 15:52'
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
- [x] #1 Create scripts/generate_confusion_matrix.py
- [x] #2 Load ground truth and OCR predictions on the test set
- [x] #3 Perform character-level alignment to identify insertions, deletions, and substitutions
- [x] #4 Generate a formatted confusion matrix (CSV/Markdown) of the top confused character pairs
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully created and executed the scripts/generate_confusion_matrix.py script. It performs high-performance character-level sequence alignment via Levenshtein DP backtracking to identify exact substitutions, deletions, and insertions. It generated both a comprehensive 2D CSV confusion matrix and a beautiful, actionable Markdown analysis report highlight top syllables confused (such as Ꮧ vs Ꮨ) and high-deletion-rate characters (such as Ꭽ with 31% deletion).
<!-- SECTION:FINAL_SUMMARY:END -->

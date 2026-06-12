---
id: TASK-48
title: Investigate extracting multiple LSTM candidate predictions for robust search
status: To Do
assignee: []
created_date: '2026-06-12 21:53'
labels: []
dependencies: []
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate extracting multiple predictions from the Tesseract LSTM model using alternative path extraction or 'temperature-like' sampling. The goal is to generate a set of candidate predictions for each word to improve full-text search recall, especially for noisy OCR where the top-1 prediction might contain minor errors but candidates might be correct. This will support a future full-text search implementation that checks all generated options.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Research Tesseract configurations for alternative LSTM predictions (e.g., lstm_choice_mode)
- [ ] #2 Implement a spike script that extracts the top-N word candidates for a sample of lines
- [ ] #3 Evaluate the improvement in 'correct word capture' when using top-N candidates vs top-1
- [ ] #4 Propose an architecture for storing and searching these candidates in the system
<!-- AC:END -->

---
id: TASK-48
title: Investigate extracting multiple LSTM candidate predictions for robust search
status: Done
assignee:
  - '@myself'
created_date: '2026-06-12 21:53'
updated_date: '2026-06-15 23:38'
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
- [x] #1 Research Tesseract configurations for alternative LSTM predictions (e.g., lstm_choice_mode)
- [x] #2 Implement a spike script that extracts the top-N word candidates for a sample of lines
- [x] #3 Evaluate the improvement in 'correct word capture' when using top-N candidates vs top-1
- [x] #4 Propose an architecture for storing and searching these candidates in the system
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Evaluated multiple LSTM candidate predictions. Relative recall improvement (Top-2 vs Top-1) is 11.41% (from 37.70% to 42.01%). Top-5 capture rate is 45.29%. Standardized implementation code saved to scripts/spike_lstm_candidates.py. Proposed storage architecture: store top-N candidate choices per word as a JSON array or index multi-valued terms in full-text engine (e.g. SQLite FTS).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated and implemented multiple LSTM candidate word predictions using Tesseract's  and parsed hOCR via BeautifulSoup. Generated top-N candidate words using Cartesian candidate generation sorted by sum of joint character confidences. Evaluated candidate accuracy against 100 Cherokee ground truth crops. Found that Top-2 candidates improve correct word capture rate from 37.70% (Top-1) to 42.01%, yielding a relative recall improvement of 11.41%. Top-5 candidates further improved recall to 45.29%.
<!-- SECTION:FINAL_SUMMARY:END -->

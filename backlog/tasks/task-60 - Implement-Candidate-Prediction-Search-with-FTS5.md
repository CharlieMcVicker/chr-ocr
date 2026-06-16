---
id: TASK-60
title: Implement Candidate Prediction Search with FTS5
status: Done
assignee:
  - '@self'
created_date: '2026-06-15 23:46'
updated_date: '2026-06-15 23:47'
labels: []
dependencies: []
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create search_candidates.py script using pytesseract lstm_choice_mode=2 and sqlite3 FTS5 to index top-2 word predictions for line crops from the manifest, and verify robustness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create scripts/search_candidates.py using FTS5
- [x] #2 Load manifest, crop lines, extract top-2 word candidates
- [x] #3 Store and index space-separated top-2 candidates in FTS5 table
- [x] #4 Provide build and search command line interfaces
- [x] #5 Verify search of a word only captured in top-2 candidates
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented scripts/search_candidates.py. Symlinked the Python virtual environment (.venv) and dataset directory under training_data_v2/dataset. Successfully built candidates.db indexing Cherokee candidates. Verified search functionality using the word 'ᏚᏨᏘᎸᏎᎾᏁ' which was captured as a top-2 alternative.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created the scripts/search_candidates.py script using Python sqlite3 FTS5 module. It parses hOCR output from pytesseract run with lstm_choice_mode=2, generates Cartesian-product word candidates limited to top-2 options, and indexes them in an SQLite FTS5 table alongside metadata. Tested by building the DB on a subset of 50 lines and performing a search on a top-2 word candidate 'ᏚᏨᏘᎸᏎᎾᏁ', which successfully returned the matching line ID and metadata.
<!-- SECTION:FINAL_SUMMARY:END -->

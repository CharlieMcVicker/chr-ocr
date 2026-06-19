---
id: TASK-88
title: Fix hyphenation duplicate-word alignment bug
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 14:03'
updated_date: '2026-06-17 14:04'
labels: []
dependencies: []
ordinal: 93000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The alignment logic misidentifies the hyphen split when duplicate words occur in a verse because the search pointer does not advance on non-hyphenated lines. We need to extract the hyphenation logic, write a debug script, track line-by-line progress to advance the search pointer, and align the New Testament crops correctly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Refactor scripts/align_verses.py to extract preprocess_hyphenated_words
- [x] #2 Create scratch/debug_hyphenation.py to trace the Matthew 1:5 case
- [x] #3 Correct the hyphenation match logic to advance start_search_idx using non-hyphenated line matches
- [x] #4 Verify that aligned_manifest.json is correctly updated and all alignments build
<!-- AC:END -->



## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored scripts/align_verses.py to extract modular preprocess_hyphenated_words logic, created scratch/debug_hyphenation.py to trace Matthew 1:5, and corrected search pointer tracking logic to prevent overshooting identical words on subsequent lines by sequentially advancing the pointer on non-hyphenated lines with early breaks for close matches.
<!-- SECTION:FINAL_SUMMARY:END -->

---
id: TASK-202
title: >-
  Update charset and ground-truth text normalization to support missing
  characters and ASCII quotes
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 23:49'
updated_date: '2026-07-21 23:49'
labels: []
dependencies: []
ordinal: 208000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update REQUIRED_CHARACTERS in phoenix/training/charset.py to include missing Cherokee characters (Ꮌ, Ꮊ, Ꮍ, Ꮛ, Ᏽ, ᏶, ᏷, ᏾, double quotes) and update normalization to replace fancy quotes with ASCII quotes (' and ").
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update REQUIRED_CHARACTERS in phoenix/training/charset.py
- [x] #2 Update ground-truth normalization to map curly quotes to ASCII quotes (' and ")
- [x] #3 Verify all unit tests pass cleanly
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated REQUIRED_CHARACTERS in phoenix/training/charset.py to include missing Cherokee characters (Ꮌ, Ꮊ, Ꮍ, Ꮛ, Ᏽ, ᏶, ᏷, ᏾) and ASCII quotes (' and "). Updated phoenix/text/normalization.py to replace curly/fancy quotes with standard ASCII quotes.
<!-- SECTION:FINAL_SUMMARY:END -->

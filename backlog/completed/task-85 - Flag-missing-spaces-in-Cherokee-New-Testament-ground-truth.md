---
id: TASK-85
title: Flag missing spaces in Cherokee New Testament ground truth
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 13:51'
updated_date: '2026-06-17 13:53'
labels:
  - data
  - ocr
dependencies: []
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
During ground-truth to line crop alignment, we found instances where the ground-truth text (e.g. verse 20: ᏄᏍᏕᎠᏓᏅᏖᏍᎨᎢ) contains a missing space typo compared to how the OCR model and language rules want to read it (e.g. ᏄᏍᏕ ᎠᏓᏅᏖᏍᎨᎢ). We need to identify, flag, or resolve these missing spaces (possibly where both stock and FTM models agree to split the word with high confidence) so that we can correct the training set or flag them for human review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement utility or flag to detect words in ground truth that the model confidently splits into two
- [x] #2 Identify missing space candidates where both stock and FTM models agree on a split (space insertion)
- [x] #3 Generate a JSON/CSV report of proposed space corrections for human approval
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
We will create a script  which:
1. Loads  from the CNT books (e.g. ).
2. Iterates over all verses and their line-level OCR predictions (both  and ).
3. Specifically scans the raw OCR predictions for words. For each word in the ground truth, we can check if both  and  split that ground truth word into two distinct parts separated by a space (e.g., ground-truth has , but both raw OCRs have  and  or close variants with a space). We can align or match substring splits to detect this.
4. Generates a JSON report  containing the verse key, the original ground truth word, the suggested split, and the evidence (what stock and FTM OCR read).
5. Runs the script on book_01 and outputs the candidate report for review.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created utility script at scripts/find_missing_spaces.py which compares GT words against raw OCR outputs from both stock and FTM models. It flags missing spaces (typos in the GT where both models agree on a split within a line or across a line without a hyphen) and outputs candidates to a JSON report at training_data/cnt/book_01/missing_spaces_candidates.json. Running this on Matthew (book_01) successfully identified the exact missing space typo in verse 20 ('ᏄᏍᏕᎠᏓᏅᏖᏍᎨᎢ,' -> 'ᏄᏍᏕ ᎠᏓᏅᏖᏍᎨᎢ,') with zero false positives.
<!-- SECTION:FINAL_SUMMARY:END -->

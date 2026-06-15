---
id: TASK-8
title: Refactor File Processing Pipeline and Integrate Doxa Binarization
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-10 14:33'
labels: []
dependencies: []
modified_files:
  - server/process_file.py
  - server/binarizer.py
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor server/process_file.py to separate concerns, and update server/binarizer.py to integrate background subtraction, bilateral filtering, connected components denoising, and Doxa local binarization models.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Provide a clean single-responsibility interface for file processing in server/process_file.py
- [x] #2 Integrate Doxa binarization models (Su, Sauvola, Wolf) in server/binarizer.py
- [x] #3 Add background subtraction and morphological cleanup for illumination correction
- [x] #4 Add connected components-based noise removal for binary outputs
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refactor server/process_file.py into reusable helper functions\n2. Add preprocess_and_binarize_cv2 core binarization helper in server/binarizer.py\n3. Add background subtraction and morph cleanup\n4. Add connected component filtering
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored server/process_file.py into small, single-responsibility functions. Enhanced server/binarizer.py with cv2 preprocessing (background subtraction, bilateral filtering, connected components cleanup) and in-memory binarization.
<!-- SECTION:FINAL_SUMMARY:END -->

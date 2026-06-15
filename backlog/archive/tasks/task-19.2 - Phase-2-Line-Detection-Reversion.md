---
id: TASK-19.2
title: 'Phase 2: Line Detection Reversion'
status: Done
assignee: []
created_date: '2026-06-10 20:14'
updated_date: '2026-06-10 20:21'
labels: []
dependencies: []
parent_task_id: TASK-19
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Revert to Surya DetectionPredictor for line extraction instead of Tesseract.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update `scripts/prepare_training_data.py` and `scripts/extract_lines.py` to stop using `get_tesseract_line_bboxes`.\n2. Import `load_model`, `load_processor` from `surya.model.detection.segformer` and `batch_text_detection` from `surya.detection`.\n3. Use Surya `DetectionPredictor` to detect lines in the column crops instead of Tesseract.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced Tesseract line detection with Surya DetectionPredictor in scripts/prepare_training_data.py and scripts/extract_lines.py as requested. Used SuryaInferenceManager and DetectionPredictor based on the currently installed Surya version to ensure compatibility.
<!-- SECTION:FINAL_SUMMARY:END -->

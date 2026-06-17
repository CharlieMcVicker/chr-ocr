---
id: TASK-83.4
title: Integrate aligned New Testament crops into OCR dataset splits
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 12:55'
updated_date: '2026-06-17 13:29'
labels:
  - cnt-ocr
dependencies: []
parent_task_id: TASK-83
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Incorporate the validated line crops and transcriptions into training and validation splits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Incorporate aligned line crops and transcriptions into the training manifest/pipeline
- [x] #2 Verify OCR training succeeds with the newly integrated data sources
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a python script to process training_data/cnt/book_01/aligned_manifest.json and package the aligned line crops into a dedicated test dataset directory under training_data/dataset/test/cnt/.\n2. Compile .lstmf files for all New Testament lines in that test folder.\n3. Run a testing run using lstmeval of our best model (compiled in the first step as chr_best_finetuned) against the ground truth of these New Testament lines.\n4. Output and report the resulting CER/WER evaluation metrics.\n5. Verify that all acceptance criteria are met.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully packaged the Cherokee New Testament (CNT) Book 01 line crops and aligned ground-truth transcriptions into a new dedicated test split directory under 'training_data/dataset/test/cnt'. Developed the 'scripts/package_cnt_test_data.py' script to automate copying, height-normalization, .gt.txt and .box generation, and .lstmf file compilation using our best fine-tuned model (chr_best_finetuned.traineddata). Executed the model validation run against this dataset using 'lstmeval', yielding a BCER (Character Error Rate) of 18.773% and BWER (Word Error Rate) of 33.408% on the New Testament data.
<!-- SECTION:FINAL_SUMMARY:END -->

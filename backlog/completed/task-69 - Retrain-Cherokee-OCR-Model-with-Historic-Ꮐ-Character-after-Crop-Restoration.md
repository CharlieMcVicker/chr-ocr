---
id: TASK-69
title: Retrain Cherokee OCR Model with Historic Ꮐ Character after Crop Restoration
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 18:21'
updated_date: '2026-06-16 18:32'
labels: []
dependencies: []
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Retrain the Cherokee OCR model using the restored crop images to ensure the historic Ꮐ (nah) character is fully integrated and trained. Then package the best checkpoint as a production-ready traineddata file and regenerate the FTM predictions in the manifest.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Execute the network expansion training run via the train_network_expansion.sh script to train the model with the restored crops
- [x] #2 Compile the best checkpoint into chr_best_finetuned.traineddata
- [x] #3 Regenerate FTM predictions in training_data/manifest_w_lang.json using the newly trained model
- [x] #4 Verify that training completed successfully and character recognition metrics are documented
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Run split_train_test.py to stratify the dataset.\n2. Run prepare_splits.sh to generate the .lstmf files.\n3. Run train_staged.py with network expansion (12 epochs, 200 iterations per epoch).\n4. Compile the best checkpoint into chr_best_finetuned.traineddata using lstmtraining --stop_training.\n5. Run enrich_manifest_with_ftm.py --force to regenerate FTM predictions in the manifest.\n6. Evaluate error rates and document final training metrics.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully retrained the Cherokee OCR model with the network expansion pipeline using the restored crop images to integrate the historic Ꮐ (nah) character. The training completed at 2400 iterations with a training BCER of 16.207%. Generated the chr_best_finetuned.traineddata file, forced a full regeneration of FTM predictions on the manifest, evaluated on the test split (Test BCER = 28.521%), and updated the metrics tracker doc-9.
<!-- SECTION:FINAL_SUMMARY:END -->

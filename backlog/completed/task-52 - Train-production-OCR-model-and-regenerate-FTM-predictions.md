---
id: TASK-52
title: Train production OCR model and regenerate FTM predictions
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-15 16:50'
updated_date: '2026-06-15 17:04'
labels: []
dependencies: []
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Perform a full production training run using the Staged Epoch Loop with the optimum parameters (8 epochs, 3 variations/image, 200 iterations/epoch, 0.05 error rate), package the best checkpoint, and regenerate FTM predictions/confidence scores in the manifest for the labeling interface.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Train the model using train_staged.py with optimum parameters (8 epochs, 3 variations, 200 iterations, 0.05 error rate)
- [x] #2 Verify training loss/BCER matches or improves on the run 10 trial run (~19.598% BCER)
- [x] #3 Package the best checkpoint to chr_best_finetuned.traineddata
- [x] #4 Regenerate FTM predictions and confidence scores in manifest_w_lang.json using scripts/enrich_manifest_with_ftm.py --force
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Run train_staged.py with optimal parameters: total-epochs=8, variations-per-image=3, iterations-per-epoch=200, error-rate=0.05.
2. Confirm the best checkpoint converges to a performance similar to the trial (~19.6% BCER).
3. Package the best checkpoint into training_data_v2/dataset/model/chr_best_finetuned.traineddata.
4. Run scripts/enrich_manifest_with_ftm.py with --force to regenerate all FTM predictions and confidence scores.
5. Verify manifest updates.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Trained production OCR model using train_staged.py with optimal meta-parameters: 8 epochs, 3 variations/image, 200 iterations/epoch, and 0.05 error rate. The training completed successfully, and the best checkpoint (chr_29.917_1517_1600.checkpoint) was evaluated on the 30 test splits, converging to a mean BCER of 15.547% (an improvement over the trial's 19.598%). This best model checkpoint was packaged into training_data_v2/dataset/model/chr_best_finetuned.traineddata. Finally, FTM predictions and word confidence scores were regenerated for all 8,072 manifest items in training_data_v2/manifest_w_lang.json using scripts/enrich_manifest_with_ftm.py --force.
<!-- SECTION:FINAL_SUMMARY:END -->

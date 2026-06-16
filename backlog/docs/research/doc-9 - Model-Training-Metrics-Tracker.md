---
id: doc-9
title: Model Training Metrics Tracker
type: other
created_date: '2026-06-11 14:58'
updated_date: '2026-06-16 07:40'
---
# Model Training Metrics Tracker

This document tracks the iterative improvements in the Cherokee Tesseract LSTM character error rate (BCER) as more human-labeled data is added to the training pipeline.

## Iteration History

| Date | Labeled Items | Max Iterations | Train BCER | Best Checkpoint | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 | 32 | — | 35.618% | — | First end-to-end grid search run. Base grayscale significantly outperformed all binarizations. Test BCER: 41.415% base, 46.061% Sauvola w35/k0.1. |
| 2026-06-11 | 97 | — | 43.769% | — | Updated dataset split to stratified every-nth for representation. Test accuracy drastically improved. Test BCER: 34.251% base, 33.125% Sauvola w45/k0.1. Binarization beat base by 1.1%. |
| 2026-06-11 | 2400 | 400 | (overfitting) | — | 400-iteration run showed signs of overfitting. Scaled back to 200 iterations. |
| 2026-06-11 | 2400 (Split 80/20) | 200 | 38.889% | `chr_38.889_195_200.checkpoint` | 200-iteration LSTM fine-tuning on full labeled dataset (2400 .lstmf files). RMS dropped from 3.612% to 2.983%. BWER: 60.308%. No test split eval yet. |
| 2026-06-11 | 2400 (Split 80/20) | 200 | 39.467% | `chr_39.467_194_200.checkpoint` | Introduction of 80/20 train/test split (TASK-37). **Test BCER: 36.847%**, BWER: 64.479%. Generalization looks solid (Test BCER < Train BCER). |
| 2026-06-11 | 7728 (Split 80/20, elastic+morph aug) | 200 | 56.665% | `chr_56.665_200_200.checkpoint` | TASK-38: Added elastic distortion (3 variants, cv2.remap sinusoidal field 3-6px) and morphological ink simulation (erode×2 + dilate×2 on Otsu-binarized images). Dataset grew 3.2× (161 train sources × 12 aug variants × 4 binarizations = 7728 files). Train BCER higher due to larger dataset not fully converged at 200 iters. **Test BCER: 31.737%**, BWER: 63.364%. New best test BCER — 5.1pp improvement over previous 36.847%. |
| 2026-06-11 | 7728 (Split 80/20, elastic+morph aug) | 600 | 43.258% | `chr_43.258_577_600.checkpoint` | TASK-39: Extended training to 600 iterations on the full 7728-sample augmented dataset. **Test BCER: 24.944%**, BWER: 55.757%. Massive improvement. |
| 2026-06-12 | 300 (Split 60/40) | 1600 (8 epochs) | 29.030% | `staged_tuning/run_10_epochs_8_output/chr_29.030_1522_1600.checkpoint` | **CURRENT BEST MODEL**. Parameter sweep run 10 (epochs=8, variations=3, error_rate=0.05). **Avg Test BCER: 19.598%** (16.346% base), Avg Test BWER: 42.393% (37.546% base) across all 30 binarizations. |
| 2026-06-15 | 300 (Split 60/40) | 1600 (8 epochs) | 40.050% | `dataset_staged_output/chr_40.050_1430_1500.checkpoint` | Re-run of standard epochs=8 staged loop configuration. **Avg Test BCER: 27.471%** (23.376% base), Avg Test BWER: 51.778% (46.387% base). |
| 2026-06-16 | 300 (Split 60/40) | (Evaluation) | — | `best_checkpoint.checkpoint` vs `dataset_staged_output/...` | **TASK-63**: Direct evaluation comparison on clean/low-distortion base grayscale test set. Pre-fix best run 10 achieved **21.538% BCER**, while post-fix run achieved **23.376% BCER** (a uniform 1.8pp degradation due to more difficult augmentation constraints during training). |

## Key Observations

- **Current Best Model (Run 10 - June 12)**: The model fine-tuned on June 12 (`run_10_epochs_8`) remains the **current best performing model**, yielding **16.346% BCER / 37.546% BWER** on base grayscale test data, and an average **19.598% BCER / 42.393% BWER** across all 30 binarization conditions.
- **June 15 Training Run comparison**: Re-running the standard epochs=8 loop resulted in **23.376% BCER (base)** and **27.471% average BCER** across all binarizations. This performance change is attributed to the fixes completed in **TASK-54**, where deprecated or invalid Albumentations arguments (e.g. replacing `num_shadows_upper` with `num_shadows_limit` in `RandomShadow`, and removing `alpha_affine` from `ElasticTransform`) were corrected. Correcting these parameters enabled the dynamic data augmentation pipeline to apply the intended spatial and noise distortions correctly on-the-fly, producing a more challenging training set that shifted the convergence profile.
- **Elastic + Morphological Augmentation (TASK-38)**: Adding elastic distortion and morphological ink simulation reduced test BCER significantly.
- **BCER trend**: Plateaued at 36-39% before augmentation. Now broken through to ~19.5% average (and ~16.3% base) on test.
- **Encoding warnings**: Still skipping ~8-10% of samples due to encoding failures in the base chr.traineddata. This limits the effective training set size.

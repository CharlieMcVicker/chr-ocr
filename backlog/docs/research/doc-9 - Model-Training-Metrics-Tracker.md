---
id: doc-9
title: Model Training Metrics Tracker
type: other
created_date: '2026-06-11 14:58'
updated_date: '2026-06-18 17:35'
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
| 2026-06-16 | 7728 (Split 80/20, stratified) | 2400 (12 epochs) | 16.207% | `dataset_staged_output_full/chr_checkpoint` | Retrained model with historic Ꮐ (nah) character after crop restoration. Stratified split for rare characters. **Test BCER: 28.521%**, BWER: 44.656%. |
| 2026-06-16 | 7728 (Split 80/20, stratified) | 4000 (20 epochs) | 19.977% | `staged_tuning/run_20_long_const_output/chr_19.977_3345_3900.checkpoint` | **NEW BEST MODEL WITH EXPANDED CHARSET**. Hyperparameter sweep run 20. Constant LR 0.0005. **Avg Test BCER: 7.033%**, BWER: 15.781%. |
| 2026-06-16 | 7728 (Split 80/20, stratified) | 3200 (16 epochs) | 16.817% | `staged_tuning/run_21_step_mod_aug_output/chr_16.817_2625_3100.checkpoint` | Hyperparameter sweep run 21. Stepped decay + moderate augmentation. **Avg Test BCER: 7.037%**, BWER: 14.752% (best word-level accuracy). |
| 2026-06-18 | Mixed (0.4 ratio) | 4800 (24 epochs) | — | `run_custom_big_lr_big_decay_dr6_mx4_epoch_24` | Best Mixture Ratio Sweep Run. Staged decay, LR 0.002 decaying by 0.6 every 3 epochs. **Phoenix CER: 5.72%**, **CNT CER: 3.08%**, **Weighted CER: 3.4%**. |
| 2026-06-18 | Targeted Augment + CNT | 7200 (36 epochs) | 8.025% | `chr_8.025_3272_6100.checkpoint` | **CURRENT BEST MODEL (Task 106)**. Double variations for rare Cherokee characters and prioritized CNT oversampling. Staged decay, base LR 0.002. **Phoenix CER: 6.63%**, **CNT CER: 2.83%**, **Combined Weighted CER: 3.09%**. |

## Key Observations

- **Current Best Model (Checkpoint: `chr_8.025_3272_6100`)**: The model fine-tuned using targeted Cherokee character augmentation and prioritized CNT rare-character oversampling is the **new best performing model**, yielding record-low combined error rates: **6.63% CER** on Phoenix and **2.83% CER** on CNT (**Combined Weighted CER: 3.09%**). 
- **Learning Rate Schedules and Augmentation Tuning**: Stepped decay learning rates combined with moderate/halved augmentation intensities (`run_21`) achieved nearly identical character accuracy (**7.037% BCER**) but significantly improved word-level accuracy (**14.752% BWER**), establishing it as the preferred configuration for high-fidelity word extraction.
- **June 15 Training Run comparison**: Re-running the standard epochs=8 loop resulted in **23.376% BCER (base)** and **27.471% average BCER** across all binarizations. This performance change is attributed to the fixes completed in **TASK-54**, where deprecated or invalid Albumentations arguments (e.g. replacing `num_shadows_upper` with `num_shadows_limit` in `RandomShadow`, and removing `alpha_affine` from `ElasticTransform`) were corrected. Correcting these parameters enabled the dynamic data augmentation pipeline to apply the intended spatial and noise distortions correctly on-the-fly, producing a more challenging training set that shifted the convergence profile.
- **Elastic + Morphological Augmentation (TASK-38)**: Adding elastic distortion and morphological ink simulation reduced test BCER significantly.
- **BCER trend**: Plateaued at 36-39% before augmentation. Now broken through to ~7.0% average on test with the expanded charset.
- **Encoding warnings**: Still skipping ~8-10% of samples due to encoding failures in the base chr.traineddata. This limits the effective training set size (to be investigated in TASK-74).

## Production Recommendations

### Hyperparameter & Metaparameter Tuning
Based on the extensive sweep from `doc-11` (June 16), the optimal meta-parameter boundaries for Cherokee OCR fine-tuning under the expanded post-fix pipeline are:
- **Learning Rate**: 0.0005 (with optional stepped decay by a factor of 0.5 every 4 epochs)
- **Total Epochs**: 20 (allowing full convergence)
- **Variations per Image**: 3
- **Iterations per Epoch**: 200
- **Transcription Error Injection Rate**: 0.05
- **Augmentation Intensities**: Moderate/Halved blur (0.2), shadow (0.15), spatial distortion (0.2), dropout (0.15), bleedthrough (0.125) for best word accuracy; or Default/Robust (0.4/0.3/0.4/0.3/0.25) for extreme noise resistance.


Detailed sweep results are available in [Staged Epoch Loop Meta-parameter Tuning Summary](./experiments/doc-11%20-%20Staged-Epoch-Loop-Meta-parameter-Tuning-Summary.md).

### Binarization Optimization
Based on the grid search from `doc-8` (June 11):
- **Base (Grayscale) is STILL the reigning champion.** Retaining 8-bit continuous grayscale information is objectively better for Tesseract LSTM training than aggressive Binarization.
- If binarization is strictly required, the **Sauvola algorithm** with a **larger window size (35)** and a **lower sensitivity (k = 0.1)** is ideal.
- The Su algorithm performed terribly on Cherokee syllabary strokes.

Detailed grid results are available in [Binarization Parameter Grid Search Results](./experiments/doc-8%20-%20Binarization-Parameter-Grid-Search-Results.md).

## Historical Experiments
- [Pre-fix vs Post-fix Evaluation](./experiments/doc-12-prefix-vs-postfix-evaluation.md)

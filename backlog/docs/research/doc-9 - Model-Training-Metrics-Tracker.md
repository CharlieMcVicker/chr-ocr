---
id: doc-9
title: Model Training Metrics Tracker
type: other
created_date: '2026-06-11 14:58'
updated_date: '2026-06-11 17:04'
---
# Model Training Metrics Tracker

This document tracks the iterative improvements in the Cherokee Tesseract LSTM character error rate (BCER) as more human-labeled data is added to the training pipeline.

## Iteration History

| Date | Labeled Items | Max Iterations | Train BCER | Best Checkpoint | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 | 32 | — | 35.618% | — | First end-to-end grid search run. Base grayscale significantly outperformed all binarizations. Test BCER: 41.415% base, 46.061% Sauvola w35/k0.1. |
| 2026-06-11 | 97 | — | 43.769% | — | Updated dataset split to stratified every-nth for representation. Test accuracy drastically improved. Test BCER: 34.251% base, 33.125% Sauvola w45/k0.1. Binarization beat base by 1.1%. |
| 2026-06-11 | 2400 | 400 | (overfitting) | — | 400-iteration run showed signs of overfitting. Scaled back to 200 iterations. |
| 2026-06-11 | 2400 (Split 80/20) | 200 | 38.889% | chr_38.889_195_200.checkpoint | 200-iteration LSTM fine-tuning on full labeled dataset (2400 .lstmf files). RMS dropped from 3.612% to 2.983%. BWER: 60.308%. No test split eval yet. |
| 2026-06-11 | 2400 (Split 80/20) | 200 | 39.467% | chr_39.467_194_200.checkpoint | Introduction of 80/20 train/test split (TASK-37). **Test BCER: 36.847%**, BWER: 64.479%. Generalization looks solid (Test BCER < Train BCER). |
| 2026-06-11 | 7728 (Split 80/20, elastic+morph aug) | 200 | 56.665% | chr_56.665_200_200.checkpoint | TASK-38: Added elastic distortion (3 variants, cv2.remap sinusoidal field 3-6px) and morphological ink simulation (erode×2 + dilate×2 on Otsu-binarized images). Dataset grew 3.2× (161 train sources × 12 aug variants × 4 binarizations = 7728 files). Train BCER higher due to larger dataset not fully converged at 200 iters. **Test BCER: 31.737%**, BWER: 63.364%. New best test BCER — 5.1pp improvement over previous 36.847%. |
| 2026-06-11 | 7728 (Split 80/20, elastic+morph aug) | 600 | 43.258% | chr_43.258_577_600.checkpoint | TASK-39: Extended training to 600 iterations on the full 7728-sample augmented dataset. BCER trend: 71.075%@100 → 56.665%@200 → 52.683%@300 → 49.237%@400 → 45.621%@477 → 43.258%@577. Best checkpoint at iter 577. **Test BCER: 24.944%**, BWER: 55.757%. Massive improvement: −6.8pp test BCER (31.737% → 24.944%), −7.6pp BWER. Train BCER not yet below 40% target (still declining ~2pp/100 iters at 600); further iterations would continue improving but diminishing returns evident. |

## Key Observations

- **80/20 Split Results**: The first proper evaluation on a held-out test set (480 samples) shows a BCER of **36.847%**. This is slightly better than the final training BCER of 39.467%, suggesting the model is generalizing well and the test samples were well-represented in the training distribution.
- **Elastic + Morphological Augmentation (TASK-38)**: Adding elastic distortion and morphological ink simulation reduced **test BCER from 36.847% → 31.737%** (−5.1pp, −13.9% relative). The 3.2× dataset increase means 200 iterations no longer achieves full convergence on training data (train BCER 56.665%), but the test BCER improvement confirms the new augmentations improve generalization. A longer run (400-600 iters) is likely needed to close the train/test gap.
- **600-Iteration Run (TASK-39)**: Extending to 600 iterations on the 7728-sample dataset drove **test BCER from 31.737% → 24.944%** (−6.8pp, −21.4% relative) and **BWER from 63.364% → 55.757%** (−7.6pp). Train BCER reached 43.258% at iter 577 — not yet below the 40% AC target, but the BCER was still declining slowly (~2pp/100 iters). Test BCER improvement is strong, suggesting the augmented dataset is genuinely improving generalization. More iterations (800-1000) would likely push train BCER through 40%.
- **200 vs 400 iterations**: The 200-iteration run remains the baseline for convergence. Best checkpoint consistently found near iter 195-200.
- **BCER trend**: Plateaued at 36-39% before augmentation. Now broken through to 24.9% on test (new all-time best). Further improvements likely from more iterations (800-1000) to fully converge the 7728-sample dataset.
- **Encoding warnings**: Still skipping ~8-10% of samples due to encoding failures in the base chr.traineddata. This limits the effective training set size.

import subprocess

content = """---
id: doc-9
title: Model Training Metrics Tracker
type: other
created_date: '2026-06-11 14:58'
updated_date: '2026-06-11 16:55'
---
# Model Training Metrics Tracker

This document tracks the iterative improvements in the Cherokee Tesseract LSTM character error rate (BCER) as more human-labeled data is added to the training pipeline.

## Iteration History

| Date | Labeled Items | Max Iterations | Train BCER | Best Checkpoint | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 | 32 | — | 35.618% | — | First end-to-end grid search run. Base grayscale significantly outperformed all binarizations. Test BCER: 41.415% base, 46.061% Sauvola w35/k0.1. |
| 2026-06-11 | 97 | — | 43.769% | — | Updated dataset split to stratified every-nth for representation. Test accuracy drastically improved. Test BCER: 34.251% base, 33.125% Sauvola w45/k0.1. Binarization beat base by 1.1%. |
| 2026-06-11 | 2400 | 400 | (overfitting) | — | 400-iteration run showed signs of overfitting. Scaled back to 200 iterations. |
| 2026-06-11 | 2400 | 200 | 38.889% | chr_38.889_195_200.checkpoint | 200-iteration LSTM fine-tuning on full labeled dataset (2400 .lstmf files). RMS dropped from 3.612% to 2.983%. BWER: 60.308%. No test split eval yet. |
| 2026-06-11 | 2400 (Split 80/20) | 200 | 39.467% | chr_39.467_194_200.checkpoint | Introduction of 80/20 train/test split (TASK-37). **Test BCER: 36.847%**, BWER: 64.479%. Generalization looks solid (Test BCER < Train BCER). |

## Key Observations

- **80/20 Split Results**: The first proper evaluation on a held-out test set (480 samples) shows a BCER of **36.847%**. This is slightly better than the final training BCER of 39.467%, suggesting the model is generalizing well and the test samples were well-represented in the training distribution.
- **200 vs 400 iterations**: The 200-iteration run remains the baseline for convergence. Best checkpoint consistently found near iter 195.
- **BCER trend**: Stabilized around 36-39% for both train and test. Further improvements likely require more data or architectural changes (e.g. higher-resolution normalization or different psm).
- **Encoding warnings**: Still skipping ~8-10% of samples due to encoding failures in the base `chr.traineddata`. This limits the effective training set size.
"""

subprocess.run(["backlog", "doc", "update", "doc-9", "--content", content], check=True)

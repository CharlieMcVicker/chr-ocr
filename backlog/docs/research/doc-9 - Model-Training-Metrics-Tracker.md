---
id: doc-9
title: Model Training Metrics Tracker
type: other
created_date: '2026-06-11 14:58'
---
---

# Model Training Metrics Tracker

This document tracks the iterative improvements in the Cherokee Tesseract LSTM character error rate (BCER) as more human-labeled data is added to the training pipeline.

## Iteration History

| Date | Labeled Items | Train BCER | Test BCER (Base) | Test BCER (Best Binarization) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-06-11 | 32 | 35.618% | 41.415% | 46.061% (Sauvola w35, k0.1) | First end-to-end grid search run. Base grayscale significantly outperformed all binarizations. |
| 2026-06-11 | 97 | 43.769% | 34.251% | 33.125% (Sauvola w45, k0.1) | Updated dataset split to use stratified "every nth" to ensure perfect representation of documents across Train/Test. Test accuracy drastically improved. Binarization (Sauvola) beat base by 1.1%. |

---
id: doc-15
title: 'Model Versions: OCR vs Language Prediction'
type: other
created_date: '2026-06-16 14:24'
---


# Model Versions: OCR vs Language Prediction

This document tracks the differences between the OCR model used for primary Cherokee text transcription and the model used for line-by-line language classification (`Cherokee`, `English`, `Mixed`, `Empty`).

## Why are there two models?

Historically, the project used a single fine-tuned model (`chr_best_finetuned.traineddata`) for both:
1. Extracting FTM (Fine-Tuned Model) predictions and word-level confidences.
2. Generating a weighted confidence score in `scripts/classify_layout.py` to identify the dominant language of a crop.

However, after running an extensive meta-parameter optimization and data augmentation pipeline on the training data, the newest optimal model achieved a much lower Error Rate (12.357% average BCER) and drastically changed the distribution of character-level and word-level confidence values.

If we had dropped in the new model for both tasks, the carefully tuned threshold heuristic inside `scripts/classify_layout.py` (which weighs Cherokee model confidence, English model confidence, and character proportion) would have been broken due to the shifting confidence distributions, requiring a tedious recalibration.

## Current Configuration

To avoid retuning the heuristic, we split the responsibilities:

### 1. The Language Prediction Model (`chr_lang_prediction.traineddata`)
- **Location**: `training_data_v2/dataset/model/chr_lang_prediction.traineddata`
- **Purpose**: Used strictly by `scripts/classify_layout.py` to classify line images.
- **Origin**: This is the *old* pre-fix `chr_best_finetuned.traineddata` backup. It retains the original confidence characteristics for which the layout classification threshold was calibrated.

### 2. The Fine-Tuned OCR Model (`chr_best_finetuned.traineddata`)
- **Location**: `training_data_v2/dataset/model/chr_best_finetuned.traineddata`
- **Purpose**: Used for generating high-quality transcriptions and FTM predictions (`scripts/enrich_manifest_with_ftm.py`).
- **Origin**: This is the *new* optimal model (e.g., from `run_14_lower_lr_output`) with the lowest BCER.

By keeping the older model active strictly for layout classification, we maintain backward compatibility with our established language detection heuristics while benefiting from the most accurate transcription model available.

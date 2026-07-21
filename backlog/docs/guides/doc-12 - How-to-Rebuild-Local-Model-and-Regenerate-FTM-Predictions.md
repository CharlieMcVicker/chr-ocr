---
id: doc-12
title: How to Rebuild Local Model and Regenerate FTM Predictions
type: guide
created_date: '2026-06-15 16:39'
---

# How to Rebuild Local Model and Regenerate FTM Predictions

This guide explains how to rebuild/train the local Cherokee OCR model and regenerate the Fine-Tuned Model (FTM) predictions and confidence scores for the labeling interface.

---

## Overview

The labeling interface loads cropped line images and displays:
1. The **Ground Truth** (if labeled).
2. The **FTM OCR** predictions (`ftm_ocr`).
3. The **FTM Confidence** score (`ftm_confidence`).

When you fine-tune a new Tesseract model, you must package the best checkpoint and run the enrichment script to regenerate these predictions so that the labeling interface displays the output from your new model.

---

## Phase 1: Rebuild the Trained Local Model

All python scripts must be executed using `uv run`.

### Step 1: Run Training

Run the staged epoch loop pipeline (`phoenix.training.train_staged`), which dynamically applies augmentations (like elastic distortions and ink bleeding simulation) epoch-by-epoch while maintaining a low disk footprint.

```bash
uv run python -m phoenix.training.train_staged \
  --total-epochs 8 \
  --iterations-per-epoch 120 \
  --variations-per-image 3 \
  --error-rate 0.05
```

---

### Step 2: Package the Best Checkpoint

Tesseract outputs intermediate model checkpoints (`.checkpoint` files) during training. To compile your best checkpoint into a production-ready `.traineddata` file, use Tesseract's `lstmtraining` command with the `--stop_training` flag:

```bash
lstmtraining \
  --stop_training \
  --continue_from training_data/dataset_staged_output/chr_checkpoint \
  --traineddata training_data/dataset/model/chr.traineddata \
  --model_output training_data/dataset/model/chr_best_finetuned.traineddata
```

> [!NOTE]
> Ensure the output is named exactly `chr_best_finetuned.traineddata` and is saved in `training_data/dataset/model/`, as this is the path and model name configured in the enrichment pipeline.

---

## Phase 2: Regenerate FTM Predictions

Once the new `chr_best_finetuned.traineddata` model is packaged, you must update the master manifest file (`training_data/manifest_w_lang.json`) with new predictions.

### Step 1: Run the Enrichment Module

Run `phoenix.manifest.enrich_manifest_with_ftm` to process the images and write the updated predictions and confidence scores to the manifest.

By default, the module is **restartable** and will skip entries that already have `ftm_ocr` and `ftm_confidence` populated. To force a full regeneration of all predictions (recommended when deploying a new model), pass the `--force` flag:

```bash
# Force regeneration of all predictions:
uv run python -m phoenix.manifest.enrich_manifest_with_ftm --force
```

If you only want to process new entries that do not yet have predictions:

```bash
# Process only entries without existing predictions:
uv run python -m phoenix.manifest.enrich_manifest_with_ftm
```

This pipeline will:
- Load the manifest `manifest_w_lang.json`.
- Execute PyTesseract OCR on each Cherokee image using the new `chr_best_finetuned` model.
- Calculate the mean word-level confidence.
- Periodically save progress and output final statistics, including the lowest-confidence entries.

Once the process completes, restart your web/labeling server (if running) so the labeling interface reflects the new predictions.

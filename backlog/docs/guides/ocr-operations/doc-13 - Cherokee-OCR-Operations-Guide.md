---
id: doc-13
title: Cherokee OCR Operations Guide
type: guide
created_date: '2026-06-15 12:44'
---

# Cherokee OCR Operations Guide

This guide is the master operations manual ("README") for the Cherokee Phoenix OCR project. It details the end-to-end workflow from processing raw page scans to fine-tuning the Tesseract LSTM model, managing annotations, and deploying the model for inference in the labeling interface.

---

## Workflow Overview

The diagram below illustrates the iterative fine-tuning pipeline:

```mermaid
flowchart TD
    A[Raw Page Scans] -->|1. phoenix.tools.download_scans / layout| B(Column Crops & Lang Classification)
    B -->|2. phoenix.layout / phoenix.manifest| C(Line Crops & Initial OCR Manifest)
    C -->|3. Flask Web Server| D[Human-in-the-Loop Labeling UI]
    D -->|4. Master Manifest| E(Enriched Master Manifest: manifest_w_lang.json)
    E -->|5. phoenix.training.train_staged| F[Staged Epoch Loop Training]
    F -->|6. lstmtraining --stop_training| G(chr_best_finetuned.traineddata)
    G -->|7. phoenix.manifest.enrich_manifest_with_ftm| H[Labeling UI Pre-predictions]
    H --> D
```

---

## 1. Preparing Column and Line Data from Scans

Raw scans (JPEG 2000 format `.jp2`) are downloaded or placed in the `scans/` directory.

### Step A: Download Raw Scans (Optional)
If you have new seed URLs from the Georgia Historic Newspapers archive, you can download them using:
```bash
uv run python -m phoenix.tools.download_scans <path_to_urls_file>
```

### Step B: Process Scans and Categorize Columns
To recursively crawl the raw scans, segment columns, perform skew correction, and classify columns by language (Cherokee, English, or Other), run layout processing:
```bash
uv run python -m phoenix.layout.process_all_scans
```
This extracts layout columns into `training_data/` sorted folders.

### Step C: Extract Line Crops & Initial OCR Manifest
To segment text lines inside identified Cherokee/Mixed columns using layout detection and write initial Tesseract OCR transcription guesses to the master manifest:
```bash
uv run python -m phoenix.manifest.prepare_training_data --input-dir scans --output-dir training_data
```
*   **Language Metadata**: For each column, OCR is performed with `chr+eng` to compute character/word distributions. Columns with Cherokee content are classified by `phoenix.layout.classification` and scheduled for line extraction.
*   Once line crops are extracted, `phoenix.manifest.add_predicted_lang_to_manifest` is invoked to add specific language metadata classifications (`Cherokee`, `English`, or `Mix`) for each line crop entry:
    ```bash
    uv run python -m phoenix.manifest.add_predicted_lang_to_manifest
    ```
    This generates/updates `training_data/manifest_w_lang.json`.

---

## 2. Starting the Labeling Server

The human-in-the-loop web interface allows you to view crops, correct transcriptions, and mark lines as verified.

To run the Flask labeling server locally:
```bash
export FLASK_APP=server/app.py
export PORT=5000
uv run flask run --host=0.0.0.0 --port=$PORT
```
Open your browser and navigate to `http://localhost:5000` to start labeling. The server interacts directly with `training_data/manifest_w_lang.json`.

---

## 3. Training the Model

Training Cherokee OCR uses a **Staged Epoch Loop** pipeline (`phoenix.training.train_staged`) that applies dynamic augmentations (elastic distortions, morphological erosion/dilation) on-the-fly each epoch while keeping disk usage low.

> [!NOTE]
> The **Staged Epoch Loop** dynamically splits the dataset in-memory and compiles training `.lstmf` files on-the-fly in temporary output directories.

### Step A: Run Production Training with Best Parameters
Based on systematic parameter tuning, the optimal parameters are:
*   **Total Epochs**: 8
*   **Iterations per Epoch**: 200 (1600 iterations total)
*   **Variations per Image**: 3
*   **Synthetic Transcription Error Rate**: 0.05

Run the training loop:
```bash
uv run python -m phoenix.training.train_staged \
  --total-epochs 8 \
  --iterations-per-epoch 200 \
  --variations-per-image 3 \
  --error-rate 0.05 \
  --train-manifest training_data/manifest_w_lang.json \
  --output-dir training_data/dataset_epoch \
  --model-dir training_data/dataset/model \
  --train-output-dir training_data/dataset_staged_output
```

### Step B: How to Run Sweeps and Evaluation
To execute hyperparameter sweeps across different training configurations and evaluate character/word error rates against test splits, use the training sweep module:
```bash
uv run python -m phoenix.training.sweep
```

---

## 4. Rebuilding the Finetuned Model for Inference

Tesseract outputs model checkpoints (`.checkpoint` files) during training. To build the final inference model:

### Step A: Package the Best Checkpoint
Run `lstmtraining` with the `--stop_training` flag to convert the best checkpoint into a deployable `.traineddata` file:
```bash
lstmtraining \
  --stop_training \
  --continue_from training_data/dataset_staged_output/chr_checkpoint \
  --traineddata training_data/dataset/model/chr.traineddata \
  --model_output training_data/dataset/model/chr_best_finetuned.traineddata
```

### Step B: Add Inferences to the Labeling Server
To display predictions from your new model as interactive suggestions inside the UI:

1.  **Regenerate predictions in the manifest**:
    Use the FTM enrichment module to parse line crops using your newly packaged `chr_best_finetuned.traineddata` model:
    ```bash
    # Force recalculation of all predictions
    uv run python -m phoenix.manifest.enrich_manifest_with_ftm --force
    ```
2.  **Restart the web server**:
    Once the enrichment module finishes updating `training_data/manifest_w_lang.json`, restart the Flask web server to see the updated FTM predictions and confidence values in the interface.

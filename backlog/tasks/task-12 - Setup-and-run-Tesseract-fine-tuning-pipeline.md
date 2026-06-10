---
id: TASK-12
title: Setup and run Tesseract fine-tuning pipeline
status: To Do
assignee: []
created_date: '2026-06-10 19:06'
updated_date: '2026-06-10 19:14'
labels: []
dependencies: []
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up Tesseract fine-tuning (e.g., using tesstrain) locally on M1 Mac, with a fallback Colab notebook.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Setup tesstrain or equivalent locally on macOS M1
- [ ] #2 Run fine-tuning process locally using chr.traineddata and lstmf dataset
- [ ] #3 Create a fallback Colab notebook for training if local M1 training fails
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Goal Description

The goal of Task-12 is to execute the actual fine-tuning of the Tesseract LSTM model using our formatted Cherokee dataset. Since compiling Tesseract training tools locally on an Apple Silicon (M1) Mac can sometimes present dependency challenges, we will set up a primary local pipeline using the official `tesstrain` repository, while simultaneously preparing a bulletproof fallback Google Colab Notebook that runs in a clean Ubuntu environment.

## Proposed Changes

We will create the necessary scripts and notebooks to orchestrate the `tesstrain` Makefile process.

### Scripts & Notebooks

#### [NEW] [run_training_local.sh](file:///Users/charlesmcvicker/code/phoenix/scripts/run_training_local.sh)
This bash script will handle the local M1 pipeline:
1. Ensure prerequisite Homebrew packages are installed (`tesseract`, `cairo`, `pango`, `icu4c`).
2. Clone the official `tesseract-ocr/tesstrain` repository into a `training_env/` directory.
3. Automatically copy our `.lstmf` and `.box` files from `dataset/train/` into `training_env/data/chr-ground-truth/`.
4. Copy the downloaded `chr.traineddata` (from Task-9) into `training_env/usr/share/tessdata/`.
5. Execute the `tesstrain` Make command:
   ```bash
   make training MODEL_NAME=chr START_MODEL=chr TESSDATA=../usr/share/tessdata MAX_ITERATIONS=10000
   ```

#### [NEW] [Tesseract_FineTuning_Colab.ipynb](file:///Users/charlesmcvicker/code/phoenix/notebooks/Tesseract_FineTuning_Colab.ipynb)
A Jupyter Notebook designed specifically for Google Colab as a fallback. It will include cells to:
1. `apt-get install tesseract-ocr libtesseract-dev` (Ubuntu makes this trivial).
2. Clone the `tesstrain` repository.
3. Mount Google Drive to load our zipped dataset generated in Tasks 9-11.
4. Run the identical `make training` command on a Colab GPU, which will drastically speed up training if the local M1 CPU/GPU struggles.

## Open Questions
> [!WARNING]
> Tesseract fine-tuning on macOS M1 without Docker occasionally runs into `cairo` and `pango` pathing issues. Do you want the local script to attempt running bare-metal via Homebrew first, or should we just containerize the local training in a `Dockerfile` from the start to guarantee it works?

## Verification Plan

### Manual Verification
- Run `scripts/run_training_local.sh` and verify that the Tesseract training iterations begin outputting CER (Character Error Rate) metrics to the console.
- Open `notebooks/Tesseract_FineTuning_Colab.ipynb` in Google Colab, execute the setup cells, and verify the environment builds successfully.
<!-- SECTION:PLAN:END -->

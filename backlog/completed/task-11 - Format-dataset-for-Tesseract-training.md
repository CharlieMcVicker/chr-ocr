---
id: TASK-11
title: Format dataset for Tesseract training
status: Done
assignee: []
created_date: '2026-06-10 19:06'
updated_date: '2026-06-15 17:40'
labels: []
dependencies: []
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Convert the augmented images and labels into the required .box and .lstmf formats for Tesseract fine-tuning.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Generate .box files for augmented images
- [ ] #2 Generate .lstmf files for augmented images
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Goal Description

The goal of Task-11 is to format our augmented `.png` images and `.gt.txt` text labels into the specific formats Tesseract requires for LSTM fine-tuning: `.box` files (bounding boxes) and `.lstmf` files (Tesseract's binary training format). 

While the official `tesstrain` repository handles this under the hood, writing a standalone script to generate these ensures our pipeline is robust, reproducible, and seamlessly integrates with our custom augmentation outputs.

## Proposed Changes

We will create a Python formatting script that iterates over our newly split and augmented dataset directories (from Task-10) and processes them using Tesseract's training commands.

### Scripts

#### [NEW] [format_dataset.py](file:///Users/charlesmcvicker/code/phoenix/scripts/format_dataset.py)
This script will:
1. Iterate over every `.png` and `.gt.txt` pair in the `dataset/train/` and `dataset/test/` subdirectories.
2. **Generate `.box` files:** Since our images are single-line crops, we can programmatically generate the box file. We'll read the image dimensions (width, height) using OpenCV or PIL, and create a bounding box that encompasses the entire image, mapping it to the text from `.gt.txt`. This avoids the need for Tesseract to guess the bounding boxes.
3. **Generate `.lstmf` files:** We'll use the `subprocess` module to call Tesseract in training mode for each image:
   ```bash
   tesseract sample.png sample --psm 6 lstm.train
   ```
   *(We will use `--psm 6` which assumes a single uniform block of text, perfect for our line-crops).*
4. **Generate List Files:** Finally, the script will generate `list.train` and `list.eval` files (text files containing the paths to all the generated `.lstmf` files), which Tesseract's fine-tuning process requires to know which files to iterate over.

## Open Questions
> [!IMPORTANT]
> Tesseract must be installed on your M1 Mac for this step to work (`brew install tesseract`). Are you comfortable with us running `tesseract` commands via Python `subprocess`, or would you prefer we fully integrate the `tesseract-ocr/tesstrain` Makefile repository and let it handle `.lstmf` generation?

## Verification Plan

### Manual Verification
- Run `python scripts/format_dataset.py`.
- Check that for every `image.png`, there is now an `image.box` and `image.lstmf` file in the directory.
- Ensure the `list.train` file is populated with paths to the `.lstmf` files from the training directory.
<!-- SECTION:PLAN:END -->

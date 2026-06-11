---
id: doc-6
title: Line-By-Line Language Classification Spike Results
type: other
created_date: '2026-06-10 21:29'
updated_date: '2026-06-10 21:29'
---
# Line-By-Line Language Classification Spike Results

## Context
We investigated whether we could accurately classify the language (Cherokee vs. English) of individual line crops in "Mixed" columns using Tesseract OCR, with the goal of discarding purely English lines before the manual labeling phase.

## Approach
A spike script (`scripts/spike_line_language_classification.py`) was created to:
1. Run layout detection on `scans/1828-02-21/seq-1.jp2`.
2. Extract lines from a column classified as "Mixed".
3. Run OCR on each line crop using three different Tesseract models: `chr+eng`, `chr`, and `eng`.
4. Output a side-by-side comparison report with character counts and token metrics.

## Findings
- The results from the spike were rough. Tesseract struggled significantly, possibly due to the poor quality ("dirty") of the test image.
- Because the baseline OCR performance on these individual line crops is so noisy, relying purely on Tesseract character counts or classifications per-line to auto-filter lines may lead to false positives (discarding Cherokee text) or false negatives (keeping English junk).
- Further refinement is needed. We may need to test on cleaner images, investigate better binarization/preprocessing specifically for line crops, or rethink the heuristic before merging line-by-line filtering into the main `prepare_training_data.py` loop.

## Next Steps
- Re-evaluate line-by-line filtering when the base OCR accuracy or image quality is improved.
- For now, this is paused as we wrap up the current session.

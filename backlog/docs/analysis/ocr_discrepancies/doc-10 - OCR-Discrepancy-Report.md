---
id: doc-10
title: OCR Discrepancy Report
type: other
created_date: '2026-06-11 22:35'
---


# OCR Discrepancy Report

## Findings

I analyzed `manifest_w_lang.json` to identify discrepancies where one model predicted text but the other did not. 

Out of **8,072** total lines in the manifest:
- **144 lines** have text predicted by the Initial (baseline) OCR, but the Fine-Tuned Model (FTM) predicts absolutely nothing (empty string).
- **0 lines** have text predicted by the FTM but nothing from the Initial OCR.
- **7,928 lines** have text predicted by both models.

This indicates that our FTM is systematically more conservative or entirely dropping predictions on certain images where the baseline model hallucinates or correctly identifies faint text.

## Proposed Further Investigations

To understand why the FTM is dropping text on these 144 lines, we can investigate the following areas:

### 1. Image Quality Review
Extract and visualize a sample of the 144 cropped images (`image_path`). 
- Are these actually blank spaces, smudges, or margin noise that the baseline OCR hallucinated text on? If so, the FTM is performing *better*.
- Are they very faint or degraded genuine text? If so, the FTM might be overfitting to high-contrast text.

### 2. Language and Character Set Bias
Examine the `predicted_lang` or the specific characters the baseline model predicted for these 144 lines. 
- Are these mostly English words? If the FTM was fine-tuned heavily on Cherokee, it might be suppressing Latin characters.
- Are the baseline predictions mostly punctuation or special characters?

### 3. Bounding Box Geometry
Analyze the `line_bbox` dimensions of the 144 discrepancies compared to the rest of the dataset.
- Are these bounding boxes exceptionally small (e.g., just noise or specks) or extremely narrow?

### 4. Decoding Thresholds / Confidence
Check the `ftm_confidence` for these 144 lines.
- Did the FTM actually predict a sequence of tokens with extremely low confidence that got truncated to an empty string, or did it definitively predict the End-of-Sequence (EOS) token immediately?

### 5. Ground Truth Sampling
Generate a labeled subset of these 144 lines (e.g., 20 random samples) to establish ground truth. Send them through the labeling interface to determine definitively which model is "correct" for this specific discrepancy bucket.

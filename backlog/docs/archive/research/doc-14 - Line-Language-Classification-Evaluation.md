---
id: doc-14
title: Line-Language-Classification-Evaluation
type: research
created_date: '2026-06-15 18:20'
updated_date: '2026-06-15 18:20'
---
# Line-by-Line Language Classification Evaluation Results

## Objective
Evaluate Cherokee vs. English language classification on individual line crops, combining Tesseract OCR predictions and fine-tuned Cherokee model (FTM) confidence metrics.

## Methodology
- **Dataset**: 818 total lines:
  - 370 labeled Cherokee line crops from `chr_lines`
  - 448 labeled English line crops from `eng_lines`
  - Augmented with `not_cherokee` false positives from the labeling UX manifest (`manifest_w_lang.json`).
- **Feature Extraction**:
  - Tesseract English model confidence (`eng_conf`) and OCR transcription
  - Tesseract Cherokee model confidence (`chr_conf`) and OCR transcription
  - Fine-Tuned Cherokee Model confidence (`ftm_conf`) and OCR transcription
  - Tesseract character-count-based Cherokee percentage (`pct_cherokee = cherokee_count / (cherokee_count + latin_count)`)

## Historical Context & Evolution
- **Initial Spike**: Early attempts at line-by-line classification struggled heavily due to poor image quality and high noise in baseline Tesseract models.
- **Ratio Thresholds**: A follow-up evaluated a simple ratio threshold (`pct_cherokee`). Using strict thresholds (`> 0.45` for Cherokee, `< 0.40` for English) yielded a **99.14%** baseline.
- **Current Model**: The heuristics below build upon these early metrics by incorporating Fine-Tuned Model (FTM) confidences to achieve up to **99.76%** accuracy.

## Findings

### Weighted Heuristic
We performed a grid search to optimize a weighted confidence function:
\[
\text{Score} = w_{\text{ftm}} \cdot \text{conf}_{\text{ftm}} + w_{\text{chr}} \cdot \text{conf}_{\text{chr}} - w_{\text{eng}} \cdot \text{conf}_{\text{eng}} + w_{\text{pct}} \cdot (\text{pct\_cherokee} \times 100)
\]
**Optimal Parameters**:
* \(w_{\text{ftm}}\): 0.20
* \(w_{\text{chr}}\): 0.50
* \(w_{\text{eng}}\): 0.50
* \(w_{\text{pct}}\): 0.50
* **Threshold**: 32.1158
* **Accuracy**: **99.76%** (only 2 errors out of 818 samples)

### Rule-Based Heuristic
For simple interpretability and code maintenance, we also evaluated a decision rule:
* Classify as Cherokee if:
  * `pct_cherokee >= 0.40`
  * OR (`pct_cherokee >= 0.15` AND `ftm_conf >= 5.0` AND `chr_conf >= 5.0` AND `eng_conf < 30.0`)
* **Accuracy**: **99.39%**
* **Confusion Matrix**:
  | True \ Pred | Cherokee | English |
  | :--- | :---: | :---: |
  | **Cherokee** | 366 | 4 |
  | **English** | 1 | 447 |

## Recommendations
We will integrate the weighted score heuristic into `scripts/classify_layout.py` and `scripts/filter_manifest.py` for maximum classification precision.

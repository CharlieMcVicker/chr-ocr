---
id: doc-7
title: Tesseract Language Classification Threshold Findings
type: other
created_date: '2026-06-11 02:33'
updated_date: '2026-06-11 02:33'
---
# Tesseract Language Classification Threshold Findings

## Objective
Fine-tune the Tesseract character-level language classification thresholds for isolating Cherokee text from English text.

## Methodology
- **Dataset**: `chr_lines` (370 lines) and `eng_lines` (448 lines) containing ground-truth crops.
- **OCR Process**: Used Tesseract OCR (`--psm 7 -l chr+eng`) on each line crop.
- **Metric**: Evaluated the percentage of Cherokee characters versus Latin characters (`pct_cherokee = cherokee_count / (cherokee_count + latin_count)`).

## Findings
The evaluation script evaluated a grid of different English and Cherokee classification thresholds to maximize accuracy. 

**Results**:
- **Accuracy**: 99.14% 
- **Optimal Thresholds**:
  - `English`: `pct_cherokee < 0.40`
  - `Cherokee`: `pct_cherokee > 0.45`
  - `Mixed`: `0.40 <= pct_cherokee <= 0.45`

### Confusion Matrix
| True \ Pred | Cherokee | English | Mixed | Empty |
|-------------|----------|---------|-------|-------|
| **Cherokee**| 365      | 3       | 1     | 1     |
| **English** | 1        | 446     | 0     | 1     |

## Implementation
These thresholds have been updated in `scripts/filter_manifest.py` and `scripts/classify_layout.py` to ensure future crops are classified with this 99.14% baseline accuracy.

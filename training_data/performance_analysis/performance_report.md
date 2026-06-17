# OCR Model Performance Analysis Report

- **Checkpoint**: `training_data/dataset_staged_output_full/chr_16.457_1987_2300.checkpoint`
- **Dataset**: `training_data/dataset/test/base` (39 lines)
- **Encoding errors / missing GT**: 13 lines (CER forced to 100%)

## Overall Metrics

| Metric | Value |
| :--- | :---: |
| Mean CER (all lines) | **39.184%** |
| Mean CER (ok lines only) | **8.776%** |
| Median CER (all lines) | **12.903%** |
| lstmeval BCER (aggregate) | **10.851%** |
| lstmeval BWER | **25.244%** |

## Document-level Performance

| Document Page | Lines | Mean CER | Median CER |
| :--- | :---: | :---: | :---: |
| `1828-05-06_seq-1` | 1 | 100.00% | 100.00% |
| `1828-05-06_seq-3` | 1 | 100.00% | 100.00% |
| `1828-05-21_seq-1` | 1 | 100.00% | 100.00% |
| `1828-06-04_seq-2` | 1 | 100.00% | 100.00% |
| `1828-08-20_seq-4` | 3 | 100.00% | 100.00% |
| `1828-04-17_seq-3` | 4 | 53.52% | 53.70% |
| `1828-04-17_seq-2` | 2 | 51.85% | 51.85% |
| `1828-05-21_seq-3` | 2 | 51.85% | 51.85% |
| `1828-04-17_seq-4` | 7 | 33.24% | 10.00% |
| `1828-03-27_seq-1` | 1 | 24.00% | 24.00% |
| `1828-03-27_seq-2` | 2 | 16.13% | 16.13% |
| `1828-05-06_seq-2` | 2 | 9.82% | 9.82% |
| `1828-04-10_seq-1` | 8 | 9.49% | 7.95% |
| `1828-03-13_seq-1` | 2 | 9.33% | 9.33% |
| `1828-07-02_seq-1` | 1 | 3.57% | 3.57% |
| `1828-03-13_seq-4` | 1 | 0.00% | 0.00% |

## Top 10 Worst Performing Lines

| Base Name | Document | CER | Status |
| :--- | :--- | :---: | :--- |
| `1828-04-17_seq-2_col_00_line_009` | `1828-04-17_seq-2` | 100.00% | encoding_error |
| `1828-04-17_seq-3_col_01_line_166` | `1828-04-17_seq-3` | 100.00% | encoding_error |
| `1828-04-17_seq-3_col_01_line_178` | `1828-04-17_seq-3` | 100.00% | encoding_error |
| `1828-04-17_seq-4_col_01_line_027` | `1828-04-17_seq-4` | 100.00% | encoding_error |
| `1828-04-17_seq-4_col_01_line_087` | `1828-04-17_seq-4` | 100.00% | encoding_error |
| `1828-05-06_seq-1_col_03_line_124` | `1828-05-06_seq-1` | 100.00% | encoding_error |
| `1828-05-06_seq-3_col_01_line_156` | `1828-05-06_seq-3` | 100.00% | encoding_error |
| `1828-05-21_seq-1_col_03_line_008` | `1828-05-21_seq-1` | 100.00% | encoding_error |
| `1828-05-21_seq-3_col_01_line_006` | `1828-05-21_seq-3` | 100.00% | encoding_error |
| `1828-06-04_seq-2_col_00_line_007` | `1828-06-04_seq-2` | 100.00% | encoding_error |

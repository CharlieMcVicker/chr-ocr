# OCR Model Performance Analysis Report

- **Checkpoint**: `training_data/dataset_staged_output_full/chr_16.457_1987_2300.checkpoint`
- **Dataset**: `training_data/dataset/test/base` (39 lines)
- **Encoding errors / missing GT**: 20 lines (CER forced to 100%)

## Overall Metrics

| Metric | Value |
| :--- | :---: |
| Mean CER (all lines) | **89.709%** |
| Mean CER (ok lines only) | **78.876%** |
| Median CER (all lines) | **100.000%** |
| lstmeval BCER (aggregate) | **77.623%** |
| lstmeval BWER | **90.788%** |

## Document-level Performance

| Document Page | Lines | Mean CER | Median CER |
| :--- | :---: | :---: | :---: |
| `1828-03-27_seq-1` | 1 | 100.00% | 100.00% |
| `1828-03-27_seq-2` | 2 | 100.00% | 100.00% |
| `1828-05-06_seq-1` | 1 | 100.00% | 100.00% |
| `1828-05-06_seq-3` | 1 | 100.00% | 100.00% |
| `1828-05-21_seq-1` | 1 | 100.00% | 100.00% |
| `1828-06-04_seq-2` | 1 | 100.00% | 100.00% |
| `1828-08-20_seq-4` | 3 | 100.00% | 100.00% |
| `1828-04-17_seq-2` | 2 | 94.44% | 94.44% |
| `1828-07-02_seq-1` | 1 | 92.86% | 92.86% |
| `1828-05-06_seq-2` | 2 | 89.29% | 89.29% |
| `1828-04-17_seq-3` | 4 | 89.17% | 100.00% |
| `1828-04-17_seq-4` | 7 | 88.46% | 100.00% |
| `1828-04-10_seq-1` | 8 | 85.76% | 89.66% |
| `1828-03-13_seq-1` | 2 | 80.77% | 80.77% |
| `1828-05-21_seq-3` | 2 | 74.07% | 74.07% |
| `1828-03-13_seq-4` | 1 | 66.67% | 66.67% |

## Top 10 Worst Performing Lines

| Base Name | Document | CER | Status |
| :--- | :--- | :---: | :--- |
| `1828-03-13_seq-1_col_02_line_024` | `1828-03-13_seq-1` | 100.00% | encoding_error |
| `1828-03-27_seq-1_col_00_line_029` | `1828-03-27_seq-1` | 100.00% | ok |
| `1828-03-27_seq-2_col_00_line_000` | `1828-03-27_seq-2` | 100.00% | ok |
| `1828-03-27_seq-2_col_00_line_005` | `1828-03-27_seq-2` | 100.00% | encoding_error |
| `1828-04-10_seq-1_col_00_line_029` | `1828-04-10_seq-1` | 100.00% | ok |
| `1828-04-10_seq-1_col_03_line_138` | `1828-04-10_seq-1` | 100.00% | encoding_error |
| `1828-04-10_seq-1_col_03_line_146` | `1828-04-10_seq-1` | 100.00% | encoding_error |
| `1828-04-10_seq-1_col_03_line_156` | `1828-04-10_seq-1` | 100.00% | encoding_error |
| `1828-04-17_seq-2_col_00_line_009` | `1828-04-17_seq-2` | 100.00% | encoding_error |
| `1828-04-17_seq-3_col_01_line_008` | `1828-04-17_seq-3` | 100.00% | ok |

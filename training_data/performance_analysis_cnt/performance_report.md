# OCR Model Performance Analysis Report

- **Checkpoint**: `training_data/dataset_staged_output_full/chr_16.457_1987_2300.checkpoint`
- **Dataset**: `training_data/dataset/test/cnt` (89 lines)
- **Encoding errors / missing GT**: 34 lines (CER forced to 100%)

## Overall Metrics

| Metric | Value |
| :--- | :---: |
| Mean CER (all lines) | **44.876%** |
| Mean CER (ok lines only) | **10.799%** |
| Median CER (all lines) | **16.667%** |
| lstmeval BCER (aggregate) | **11.777%** |
| lstmeval BWER | **28.258%** |

## Document-level Performance

| Document Page | Lines | Mean CER | Median CER |
| :--- | :---: | :---: | :---: |
| `cnt_01_010114` | 3 | 100.00% | 100.00% |
| `cnt_01_010115` | 3 | 100.00% | 100.00% |
| `cnt_01_010118` | 5 | 100.00% | 100.00% |
| `cnt_01_010123` | 5 | 100.00% | 100.00% |
| `cnt_01_010109` | 3 | 70.37% | 100.00% |
| `cnt_01_010110` | 3 | 69.57% | 100.00% |
| `cnt_01_010124` | 3 | 68.63% | 100.00% |
| `cnt_01_010121` | 3 | 68.06% | 100.00% |
| `cnt_01_010125` | 2 | 55.56% | 55.56% |
| `cnt_01_010120` | 7 | 45.37% | 8.70% |
| `cnt_01_010107` | 3 | 44.95% | 18.18% |
| `cnt_01_010116` | 3 | 43.39% | 19.05% |
| `cnt_01_010104` | 3 | 42.13% | 22.22% |
| `cnt_01_010106` | 3 | 41.35% | 19.05% |
| `cnt_01_010122` | 3 | 40.56% | 16.67% |
| `cnt_01_010101` | 3 | 39.92% | 15.00% |
| `cnt_01_010119` | 4 | 33.48% | 14.69% |
| `cnt_01_010113` | 3 | 11.90% | 10.00% |
| `cnt_01_010102` | 3 | 11.19% | 15.38% |
| `cnt_01_010103` | 3 | 9.10% | 9.09% |
| `cnt_01_010111` | 3 | 8.78% | 9.09% |
| `cnt_01_010108` | 3 | 8.73% | 9.52% |
| `cnt_01_010105` | 4 | 8.52% | 4.55% |
| `cnt_01_010112` | 3 | 6.36% | 9.09% |
| `cnt_01_010117` | 8 | 5.29% | 4.55% |

## Top 10 Worst Performing Lines

| Base Name | Document | CER | Status |
| :--- | :--- | :---: | :--- |
| `cnt_01_010101_line_02` | `cnt_01_010101` | 100.00% | encoding_error |
| `cnt_01_010104_line_00` | `cnt_01_010104` | 100.00% | encoding_error |
| `cnt_01_010106_line_02` | `cnt_01_010106` | 100.00% | encoding_error |
| `cnt_01_010107_line_01` | `cnt_01_010107` | 100.00% | encoding_error |
| `cnt_01_010109_line_00` | `cnt_01_010109` | 100.00% | encoding_error |
| `cnt_01_010109_line_01` | `cnt_01_010109` | 100.00% | encoding_error |
| `cnt_01_010110_line_01` | `cnt_01_010110` | 100.00% | encoding_error |
| `cnt_01_010110_line_02` | `cnt_01_010110` | 100.00% | encoding_error |
| `cnt_01_010114_line_00` | `cnt_01_010114` | 100.00% | encoding_error |
| `cnt_01_010114_line_01` | `cnt_01_010114` | 100.00% | encoding_error |

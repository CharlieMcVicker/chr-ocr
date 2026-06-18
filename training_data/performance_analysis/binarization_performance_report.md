# Binarization Algorithm Performance Comparison Report

- **Checkpoint**: `training_data/staged_tuning/run_unicharset_finetune_output/chr_7.728_3553_6900.checkpoint`
- **Test Root Directory**: `training_data/dataset/test`
- **Number of Algorithms evaluated**: 31

## Overall Metrics by Algorithm (Evaluated Lines Only)

Sorted from lowest mean Character Error Rate (best) to highest. Encoding failures and lines missing GT are dropped from performance metrics.

| Rank | Binarization Algorithm | Mean CER | Median CER | Evaluated Lines | Dropped Lines |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `base` | **nan%** | nan% | 0/101 | 101 |
| 2 | `cnt` | **nan%** | nan% | 0/1369 | 1369 |
| 3 | `otsu` | **nan%** | nan% | 0/101 | 101 |
| 4 | `sauvola_w15_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 5 | `sauvola_w15_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 6 | `sauvola_w15_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 7 | `sauvola_w25_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 8 | `sauvola_w25_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 9 | `sauvola_w25_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 10 | `sauvola_w35_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 11 | `sauvola_w35_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 12 | `sauvola_w35_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 13 | `sauvola_w45_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 14 | `sauvola_w45_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 15 | `sauvola_w45_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 16 | `su_w15` | **nan%** | nan% | 0/101 | 101 |
| 17 | `su_w25` | **nan%** | nan% | 0/101 | 101 |
| 18 | `su_w35` | **nan%** | nan% | 0/101 | 101 |
| 19 | `su_w45` | **nan%** | nan% | 0/101 | 101 |
| 20 | `wolf_w15_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 21 | `wolf_w15_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 22 | `wolf_w15_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 23 | `wolf_w25_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 24 | `wolf_w25_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 25 | `wolf_w25_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 26 | `wolf_w35_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 27 | `wolf_w35_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 28 | `wolf_w35_k0.3` | **nan%** | nan% | 0/101 | 101 |
| 29 | `wolf_w45_k0.1` | **nan%** | nan% | 0/101 | 101 |
| 30 | `wolf_w45_k0.2` | **nan%** | nan% | 0/101 | 101 |
| 31 | `wolf_w45_k0.3` | **nan%** | nan% | 0/101 | 101 |

## Top 15 Worst-Performing Lines (Average across all algorithms)

| Rank | Base Name | Average CER | `base` | `cnt` | `otsu` | `sauvola_w15_k0.1` | `sauvola_w15_k0.2` | ... |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |

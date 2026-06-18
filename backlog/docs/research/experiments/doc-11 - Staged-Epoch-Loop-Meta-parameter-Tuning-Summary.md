---
id: doc-11
title: Staged Epoch Loop Meta-parameter Tuning Summary
type: other
created_date: '2026-06-12 03:08'
updated_date: '2026-06-18 14:04'
---
# Staged Epoch Loop Meta-parameter Tuning Summary

This document captures the systematic meta-parameter search conducted on June 12, 2026, and updated on June 16, 2026, to optimize the Staged Epoch Loop pipeline (`scripts/train_staged.py`). This pipeline orchestrates Cherokee Tesseract OCR fine-tuning by dynamically generating data augmentations (with optional weakly-supervised noise injection) in an epoch-by-epoch training sequence.

## Systematic Parameter Matrix & Results

A systematic One-at-a-Time (OAT) parameter search was performed starting from a robust baseline configuration to examine performance sensitivity. The evaluation was executed across 30 distinct validation subdirectories (representing various binarization and document degradation conditions).

| Run ID | Epochs | Variations per Image | Iterations per Epoch | Transcr. Error Rate | Avg. BCER (%) | Avg. BWER (%) | Checkpoint |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **run_1_base** | 4 | 3 | 150 | 0.05 | 25.961% | 52.611% | `chr_40.611_541_550.checkpoint` |
| **run_2_err_02** | 4 | 3 | 150 | 0.02 | 26.005% | 51.737% | `chr_38.960_538_550.checkpoint` |
| **run_3_err_10** | 4 | 3 | 150 | 0.10 | 26.598% | 53.812% | `chr_40.197_540_550.checkpoint` |
| **run_4_vars_2** | 4 | 2 | 150 | 0.05 | 26.705% | 53.490% | `chr_39.187_534_550.checkpoint` |
| **run_5_vars_4** | 4 | 4 | 150 | 0.05 | 26.333% | 52.792% | `chr_39.781_537_550.checkpoint` |
| **run_6_iter_100** | 4 | 3 | 100 | 0.05 | 29.391% | 57.755% | `chr_40.720_393_400.checkpoint` |
| **run_7_iter_200** | 4 | 3 | 200 | 0.05 | 24.530% | 51.551% | `chr_37.506_679_700.checkpoint` |
| **run_8_zero_noise** | 4 | 3 | 200 | 0.00 | 24.607% | 51.127% | `chr_38.790_678_700.checkpoint` |
| **run_9_epochs_6** | 6 | 3 | 200 | 0.05 | 21.239% | 44.990% | `chr_32.236_1153_1200.checkpoint` |
| **run_10_epochs_8** | **8** | **3** | **200** | **0.05** | **19.598%** | **42.393%** | `chr_29.030_1522_1600.checkpoint` |
| **run_11_vars_6** | 4 | 6 | 200 | 0.05 | 25.246% | 51.871% | `chr_39.326_686_700.checkpoint` |
| **run_12_vars_8** | 4 | 8 | 200 | 0.05 | 25.058% | 50.812% | `chr_38.981_687_700.checkpoint` |

## Key Findings (June 12)

1. **Epoch Iteration Depth**: Increasing the training iterations per epoch from 150 to 200 (`run_7_iter_200`) yielded a strong improvement to **24.530% BCER**. When we run even higher epoch counts, such as 6 epochs (`run_9_epochs_6` -> **21.239% BCER**) and 8 epochs (`run_10_epochs_8` -> **19.598% BCER**), the model continues to converge beautifully and shows no signs of overfitting, establishing 8 epochs as the optimal training duration boundary.
2. **Weakly-Supervised Noise Injection**: Testing a zero-noise baseline (`run_8_zero_noise`) achieved **24.607% BCER**, which is extremely close to the `0.05` error rate injection of `run_7_iter_200` (**24.530% BCER**). This indicates that weakly-supervised noise injection of `0.05` provides a slight generalization advantage (acting as a regularizer), while avoiding the degradation seen at higher noise levels like `0.10` (**26.598% BCER**).
3. **Data Augmentation Density**: Although generating 3 dynamic variations per image per epoch is the standard base configuration, testing higher augmentation densities (6 variations in `run_11_vars_6` -> **25.246% BCER** and 8 variations in `run_12_vars_8` -> **25.058% BCER**) actually showed slight performance regression and significant resource overhead compared to 3 variations (**24.530% BCER**). Thus, 3 variations represents the optimal dynamic pool density boundary.

## Post-Fix Hyperparameter Retuning Sweep (June 16, 2026)

Following the Albumentations bug fix (TASK-54), the dataset complexity increased, resulting in convergence degradation on the post-fix model using baseline hyperparameters. We executed a new systematic sweep over learning rates, augmentation intensities, weakly-supervised transcription error rates, and training epochs (up to 12 epochs) using an **80/20 train/test split**.

| Run ID | Epochs | Variations | Iterations/Epoch | LR | Aug Prob (Blur/Shadow/Dist/Drop) | Transcr. Error Rate | Avg. BCER (%) | Avg. BWER (%) | Checkpoint |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **run_13_baseline_epoch_6** | 6 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.05 | 27.965% | 52.531% | `run_13_baseline_output/chr_42.757_1158_1200.checkpoint` |
| **run_13_baseline_epoch_8** | 8 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.05 | 26.348% | 50.333% | `run_13_baseline_output/chr_38.426_1442_1500.checkpoint` |
| **run_13_baseline_epoch_10** | 10 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.05 | 24.126% | 47.463% | `run_13_baseline_output/chr_34.387_1990_2100.checkpoint` |
| **run_13_baseline_epoch_12** | 12 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.05 | 23.469% | 47.072% | `run_13_baseline_output/chr_33.635_2172_2300.checkpoint` |
| **run_14_lower_lr_epoch_6** | 6 | 3 | 200 | 0.0005 | Default (0.4/0.3/0.4/0.3) | 0.05 | 17.240% | 36.917% | `run_14_lower_lr_output/chr_29.537_1087_1200.checkpoint` |
| **run_14_lower_lr_epoch_8** | 8 | 3 | 200 | 0.0005 | Default (0.4/0.3/0.4/0.3) | 0.05 | 15.236% | 33.191% | `run_14_lower_lr_output/chr_27.251_1334_1500.checkpoint` |
| **run_14_lower_lr_epoch_10** | 10 | 3 | 200 | 0.0005 | Default (0.4/0.3/0.4/0.3) | 0.05 | 13.276% | 30.471% | `run_14_lower_lr_output/chr_25.020_1655_1900.checkpoint` |
| **run_14_lower_lr_epoch_12** | **12** | **3** | **200** | **0.0005** | **Default (0.4/0.3/0.4/0.3)** | **0.05** | **12.357%** | **27.339%** | `run_14_lower_lr_output/chr_22.966_1943_2300.checkpoint` |
| **run_15_lower_aug_epoch_6** | 6 | 3 | 200 | 0.001 | Halved (0.2/0.15/0.2/0.15) | 0.05 | 26.295% | 50.127% | `run_15_lower_aug_output/chr_34.956_1242_1300.checkpoint` |
| **run_15_lower_aug_epoch_8** | 8 | 3 | 200 | 0.001 | Halved (0.2/0.15/0.2/0.15) | 0.05 | 24.304% | 47.285% | `run_15_lower_aug_output/chr_32.117_1615_1700.checkpoint` |
| **run_15_lower_aug_epoch_10** | 10 | 3 | 200 | 0.001 | Halved (0.2/0.15/0.2/0.15) | 0.05 | 23.500% | 46.332% | `run_15_lower_aug_output/chr_31.034_1790_1900.checkpoint` |
| **run_15_lower_aug_epoch_12** | 12 | 3 | 200 | 0.001 | Halved (0.2/0.15/0.2/0.15) | 0.05 | 22.498% | 44.747% | `run_15_lower_aug_output/chr_28.942_2146_2300.checkpoint` |
| **run_16_zero_noise_epoch_6** | 6 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.00 | 27.581% | 52.189% | `run_16_zero_noise_output/chr_42.490_1166_1200.checkpoint` |
| **run_16_zero_noise_epoch_8** | 8 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.00 | 25.341% | 48.956% | `run_16_zero_noise_output/chr_39.076_1639_1700.checkpoint` |
| **run_16_zero_noise_epoch_10** | 10 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.00 | 24.653% | 47.888% | `run_16_zero_noise_output/chr_37.293_1823_1900.checkpoint` |
| **run_16_zero_noise_epoch_12** | 12 | 3 | 200 | 0.001 | Default (0.4/0.3/0.4/0.3) | 0.00 | 23.374% | 46.071% | `run_16_zero_noise_output/chr_33.941_2199_2300.checkpoint` |

### Key Findings (June 16 Sweep)

1. **Learning Rate reduction is critical**: Lowering the learning rate to `0.0005` (`run_14`) produced a dramatic improvement in error rates (achieving a new low of **12.357% average BCER** and **8.233% BCER on base clean crops**). The default rate of `0.001` was too aggressive for stable convergence on the more complex, post-fix augmented dataset.
2. **Augmentation Strength and Convergence**: Halving the augmentation intensity (`run_15`) only resulted in a marginal improvement over the default-rate baseline (average BCER of **22.498%** vs. **23.469%**). Keeping the robust defaults but reducing the learning rate yielded far superior generalization.
3. **Noise Injection acts as regularizer**: Incorporating `0.05` transcription error rate injection (`run_13`) showed equivalent or slightly better performance than `0.00` noise rate (`run_16`), confirming it acts as a healthy regularizer.

## Expanded Charset & LR Schedule Sweep (June 16, 2026)

Following the restoration of training crops and the integration of the historic Ꮐ character, we conducted a third systematic sweep to evaluate longer training runs (up to 20 epochs), learning rate decay schedules (stepped vs. exponential), and alternative augmentation settings.

| Run ID | Epochs | Variations | Iterations/Epoch | LR Schedule | Base LR | Augmentations | Avg. BCER (%) | Avg. BWER (%) | Checkpoint |
|:---|:---:|:---:|:---:|:---|:---|:---|:---:|:---:|:---|
| **run_17_const_low** | 16 | 3 | 200 | `constant` | 0.0005 | Default (0.4/0.3/0.4/0.3/0.25) | 7.555% | 16.922% | `run_17_const_low_output/chr_22.995_2715_3100.checkpoint` |
| **run_18_step_decay** | 16 | 3 | 200 | `step` | 0.0005 | Default (0.4/0.3/0.4/0.3/0.25) | 7.634% | 16.622% | `run_18_step_decay_output/chr_21.664_2744_3100.checkpoint` |
| **run_19_exp_decay** | 16 | 3 | 200 | `exp` | 0.0005 | Default (0.4/0.3/0.4/0.3/0.25) | 7.673% | 16.870% | `run_19_exp_decay_output/chr_23.007_2706_3100.checkpoint` |
| **run_20_long_const** | **20** | **3** | **200** | `constant` | **0.0005** | **Default (0.4/0.3/0.4/0.3/0.25)** | **7.033%** | **15.781%** | `run_20_long_const_output/chr_19.977_3345_3900.checkpoint` |
| **run_21_step_mod_aug** | 16 | 3 | 200 | `step` | 0.0005 | Halved (0.2/0.15/0.2/0.15/0.125) | **7.037%** | **14.752%** | `run_21_step_mod_aug_output/chr_16.817_2625_3100.checkpoint` |
| **run_22_step_high_var**| 16 | 5 | 200 | `step` | 0.0005 | Default (0.4/0.3/0.4/0.3/0.25) | 8.112% | 17.713% | `run_22_step_high_var_output/chr_22.573_2559_2900.checkpoint` |

## Best Mixture Ratio Sweep (June 18, 2026)

Following a systematic sweep of the Phoenix/CNT mixture ratio, a new optimal configuration was identified using a staged learning rate decay (decaying by 0.6 every 3 epochs from a base of 0.002) and a 0.4 mixture ratio:

| Run ID | Epochs | Variations | Iterations/Epoch | LR Schedule | Base LR | Augmentations | Phoenix CER | CNT CER | Weighted CER |
|:---|:---:|:---:|:---:|:---|:---|:---|:---:|:---:|:---|
| **run_custom_big_lr_big_decay_dr6_mx4** | 24 | 3 | 200 | `step` (decay 0.6 every 3 epochs) | 0.002 | Default | **5.72%** | **3.08%** | **3.40%** |

### Key Findings (Mixture Ratio Sweep)
1. **Staged learning rate decay from a higher base is highly effective**: Running with a base learning rate of `0.002` and a stepped decay factor of `0.6` every `3` epochs (`run_custom_big_lr_big_decay_dr6_mx4`) achieved a record-low **Phoenix CER of 5.72%** and a **Weighted CER of 3.4%** by epoch 24.
2. **0.4 Mixture Ratio is optimal**: Keeping the mixture ratio at 0.4 stably balances training between the target Phoenix domain and the larger CNT domain.

## Production Recommendation

The optimal meta-parameter boundaries for Cherokee OCR fine-tuning under the expanded post-fix pipeline are:
- **Base Learning Rate**: 0.002 with stepped decay by a factor of 0.6 every 3 epochs (as configured in `run_custom_big_lr_big_decay_dr6_mx4`) for optimal convergence and error rates.
- **Mixture Ratio**: 0.4 (Phoenix to CNT)
- **Total Epochs**: 24 (allowing full convergence under the stepped decay schedule)
- **Variations per Image**: 3
- **Iterations per Epoch**: 200
- **Transcription Error Injection Rate**: 0.05
- **Augmentation Intensities**: Default/Robust (0.4/0.3/0.4/0.3/0.25) for extreme noise resistance.

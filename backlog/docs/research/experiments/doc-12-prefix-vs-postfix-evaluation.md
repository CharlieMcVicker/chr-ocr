# Research: Pre-Fix vs. Post-Fix Model Comparison

This document provides a comparative analysis of the Tesseract OCR Cherokee models before and after fixing the Albumentations data augmentation arguments (TASK-54).

## Overview
- **Pre-Fix Model Checkpoint**: Fine-tuned on June 12 with run 10 (base validation BCER 16.346%, avg 19.598% on test). Checkpoint: `training_data_v2/staged_tuning/run_10_epochs_8_output/chr_39.119_1551_1600.checkpoint` (aliased as `best_checkpoint.checkpoint`).
- **Post-Fix Model Checkpoint**: Fine-tuned on June 15/16 with corrected Albumentations (base validation BCER 23.376%, avg 27.471% on test). Checkpoint: `training_data_v2/dataset_staged_output/chr_40.050_1430_1500.checkpoint`.

We evaluated both models on the **low-distortion (clean/base grayscale) test crop dataset** and across the various binarization algorithm outputs to isolate whether generalization improved or if there was actual performance degradation.

---

## Detailed Results Comparison

| Binarization / Image Type | Pre-Fix (Run 10) BCER / BWER | Post-Fix (Run 15/16) BCER / BWER | Performance Delta (BCER) |
| :--- | :---: | :---: | :---: |
| **base** (Clean grayscale) | **21.538%** / 44.298% | **23.376%** / 46.387% | +1.838pp (degraded) |
| **otsu** | **24.720%** / 48.264% | **26.390%** / 49.494% | +1.670pp (degraded) |
| sauvola_w15_k0.1 | 25.287% / 48.958% | 26.582% / 53.038% | +1.295pp (degraded) |
| sauvola_w15_k0.2 | 28.365% / 51.476% | 30.524% / 54.272% | +2.159pp (degraded) |
| sauvola_w15_k0.3 | 33.729% / 56.409% | 34.781% / 58.111% | +1.052pp (degraded) |
| sauvola_w25_k0.1 | 25.305% / 49.446% | 26.606% / 50.962% | +1.301pp (degraded) |
| sauvola_w25_k0.2 | 28.326% / 54.077% | 29.660% / 54.419% | +1.334pp (degraded) |
| sauvola_w25_k0.3 | 31.868% / 55.446% | 33.119% / 56.554% | +1.251pp (degraded) |
| sauvola_w35_k0.1 | 23.611% / 46.214% | 25.036% / 48.446% | +1.425pp (degraded) |
| sauvola_w35_k0.2 | 27.420% / 51.440% | 29.363% / 53.933% | +1.943pp (degraded) |
| sauvola_w35_k0.3 | 31.535% / 53.990% | 32.813% / 57.153% | +1.278pp (degraded) |
| sauvola_w45_k0.1 | 23.564% / 45.534% | 25.134% / 47.883% | +1.570pp (degraded) |
| sauvola_w45_k0.2 | 26.174% / 49.696% | 28.420% / 51.786% | +2.246pp (degraded) |
| sauvola_w45_k0.3 | 31.580% / 54.288% | 32.555% / 55.992% | +0.975pp (degraded) |
| su_w15 | 25.659% / 48.385% | 28.068% / 50.181% | +2.409pp (degraded) |
| su_w25 | 26.038% / 48.105% | 27.938% / 51.460% | +1.900pp (degraded) |
| su_w35 | 25.645% / 46.550% | 27.651% / 52.075% | +2.006pp (degraded) |
| su_w45 | 25.724% / 48.274% | 27.682% / 53.222% | +1.958pp (degraded) |
| wolf_w15_k0.1 | 24.431% / 50.601% | 26.350% / 53.349% | +1.919pp (degraded) |
| wolf_w15_k0.2 | 24.818% / 49.496% | 26.475% / 51.593% | +1.657pp (degraded) |
| wolf_w15_k0.3 | 26.369% / 50.839% | 27.816% / 53.002% | +1.447pp (degraded) |
| wolf_w25_k0.1 | 24.242% / 49.230% | 25.747% / 51.387% | +1.505pp (degraded) |
| wolf_w25_k0.2 | 23.976% / 48.345% | 25.655% / 52.353% | +1.679pp (degraded) |
| wolf_w25_k0.3 | 25.128% / 49.250% | 26.209% / 49.764% | +1.081pp (degraded) |
| wolf_w35_k0.1 | 23.223% / 46.901% | 25.200% / 49.730% | +1.977pp (degraded) |
| wolf_w35_k0.2 | 23.224% / 46.109% | 25.549% / 49.169% | +2.325pp (degraded) |
| wolf_w35_k0.3 | 22.693% / 46.968% | 24.602% / 49.621% | +1.909pp (degraded) |
| wolf_w45_k0.1 | 22.644% / 45.776% | 24.930% / 49.452% | +2.286pp (degraded) |
| wolf_w45_k0.2 | 23.281% / 45.901% | 25.598% / 48.808% | +2.317pp (degraded) |
| wolf_w45_k0.3 | 22.331% / 46.591% | 24.297% / 49.736% | +1.966pp (degraded) |
| **Average Across All** | **25.617%** | **27.471%** | **+1.854pp (degraded)** |

---

## Analysis & Takeaways

1. **Uniform Performance Degradation**: The post-fix model performs **consistently worse** across all 30 evaluation sets, showing an average degradation of **+1.854pp** in BCER. On clean grayscale (`base`), the degradation is **+1.838pp**.
2. **Generalization vs. Training Complexity**: The Albumentations bug fix corrected parameter issues (e.g. `num_shadows_limit`, removing invalid `alpha_affine` from `ElasticTransform`), making the training data harder. Rather than improving robustness and generalizability, the additional complexity seems to have slightly degraded convergence at the current training duration (1500/1600 iterations). 
3. **Recommendation**: We should consider either increasing training iteration limits to allow convergence under the more challenging augmentation setup, or dialing back the intensity of the noise/shadow parameters to find a better middle ground.

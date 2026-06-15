---
id: TASK-38
title: Add elastic distortion and morphological ink simulation augmentations
status: Done
assignee:
  - '@agent'
created_date: '2026-06-11 16:52'
updated_date: '2026-06-11 16:59'
labels: []
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Our training data consists of historical Cherokee Phoenix newspaper scans. The current augmentation pipeline (augment_dataset.py) only applies small rotations and Gaussian noise. The real scan distribution includes paper warp, ink bleed, and ink fade artifacts that the model has never seen during training. This task adds two high-impact augmentation families: (1) elastic distortion to simulate paper warp/curl, and (2) morphological erosion/dilation to simulate ink bleed and fade. These should be integrated as additional variation passes in augment_dataset.py alongside existing geometry and noise augmentations. The augmented samples should be regenerated and a new training run dispatched to measure BCER improvement.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Elastic distortion augmentation is implemented using a sinusoidal or random displacement field (e.g. via cv2.remap) that locally warps text lines to simulate paper curl
- [x] #2 Morphological ink simulation is implemented: cv2.erode for ink bleed (stroke thickening) and cv2.dilate for ink fade (stroke thinning), applied stochastically with randomised kernel sizes
- [x] #3 Both augmentation types are integrated into augment_dataset.py alongside existing rotation and noise passes, producing additional named variation entries (e.g. elastic_0, erode_0, dilate_0)
- [x] #4 augment_dataset.py is re-run to regenerate the full training dataset with the new augmentations included
- [x] #5 A training run is dispatched using the updated dataset and the resulting train BCER and test BCER are recorded in doc-9
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement augment_elastic_distortion(image) function using cv2.remap with sinusoidal+random displacement fields (amplitude 3-6px), producing 2-3 named elastic_N variants\n2. Implement augment_morphological_ink(image) function: detect binary images, apply cv2.erode with 2x2/3x3 kernel (erode_N) and cv2.dilate with 2x2 kernel (dilate_N), 1-2 variants each\n3. Integrate both new functions into augment_geometry_and_noise() return list in augment_dataset.py\n4. Re-run augment_dataset.py via venv to regenerate the full training dataset\n5. Dispatch subagent to run train_v2.sh 200 iterations + evaluate_v2.sh and record metrics in doc-9
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC 1-3 complete: implemented augment_elastic_distortion (cv2.remap, sinusoidal+blurred random field, 3 variants) and augment_morphological_ink (erode/dilate on binary images, 2+2 variants). Both integrated into augment_geometry_and_noise. Syntax verified.

Dataset regenerated: 161 train / 39 test items. New train set = 7,728 .png files (vs 2,400 before) — 3.2x increase due to elastic and morphological variants.

Training complete: output_200_20260611_115545. Train BCER 56.665% (larger dataset, not fully converged). Test BCER 31.737% — new best, -5.1pp improvement over previous 36.847%. Metrics recorded in doc-9.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
## TASK-38: Elastic Distortion + Morphological Ink Simulation Augmentations

### What was implemented

Two new augmentation functions were added to scripts/augment_dataset.py:

**augment_elastic_distortion(image)**
- Uses cv2.remap with a displacement field combining sinusoidal waves (0.5–1.5 cycles/image, random phase) and a blurred Gaussian random component
- Amplitude: 3–6 px per variant (gentle paper-curl warp, text remains legible)
- Produces 3 named variants per image: elastic_0, elastic_1, elastic_2

**augment_morphological_ink(image)**
- Guards: only applied when >90% of pixels are 0 or 255 (binary image)
- Ink bleed simulation: cv2.erode with randomly chosen 2×2 or 3×3 kernel (2 variants: erode_0, erode_1)
- Ink fade simulation: cv2.dilate with randomly chosen 2×2 or 3×3 kernel (2 variants: dilate_0, dilate_1)
- In augment_geometry_and_noise(), images are Otsu-binarized before passing to this function

**Integration into augment_geometry_and_noise()**
- Total variants per source image: 12 (base + 3 rot + noise + 3 elastic + 4 morph)
- Each variant passes through 4 binarization algorithms → 48 training files per source image
- Dataset grew from 2,400 → 7,728 training PNGs (3.2× increase, 161 source train images)

### Results

| Metric | Before (TASK-37) | After (TASK-38) | Delta |
|--------|-----------------|-----------------|-------|
| Train BCER | 39.467% | 56.665% | +17.2pp (expected — dataset 3.2× larger, 200 iters not enough to converge) |
| Test BCER | 36.847% | 31.737% | **−5.1pp (−13.9% relative improvement)** |
| Test BWER | 64.479% | 63.364% | −1.1pp |

### Conclusion

The augmentations successfully broke through the 36-39% BCER plateau, achieving a new best test BCER of 31.737%. The higher train BCER indicates the model needs more iterations to converge on the larger dataset — a follow-up task for 400-600 iteration training is recommended.
<!-- SECTION:FINAL_SUMMARY:END -->

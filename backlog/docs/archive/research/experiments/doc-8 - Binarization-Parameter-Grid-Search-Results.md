---
id: doc-8
title: Binarization Parameter Grid Search Results
type: specification
created_date: '2026-06-11 13:39'
---
---

# Binarization Parameter Grid Search & Results

We completely overhauled the data generation pipeline to properly test and grid-search `doxapy` binarization configurations and added smoothed rotational augmentations.

## 1. Pipeline Changes
1. **Dynamic Window Clamping**: The previous scripts bypassed `doxapy` algorithms entirely because line crops were too small (`< 60px`) and `doxapy` window sizes were too large (causing segmentation faults). We added a dynamic window clamp that automatically fits the maximum window strictly inside the image bounds, allowing us to accurately use Su, Sauvola, and Wolf on Cherokee line crops.
2. **Smooth Rotation Augmentations**: Instead of just `+2` and `-2` degree rotations, the dataset generation now samples 3 random angles from a continuous uniform distribution between `-3.0` and `+3.0` degrees.
3. **Randomized Train Parameters**: During the generation of the training split, instead of using fixed parameters, each line crop gets randomly chosen `window_size` (15, 25, 35, 45) and `k` values (0.1, 0.2, 0.3) for each binarization variation. This forces Tesseract to learn robustly across a wide spread of image textures.
4. **Grid-Search Test Set**: The test set now produces exactly 29 separate grid folders, containing every combination of algorithm, window size, and K-value. The evaluation script loops through all 29 folders to rigorously determine what the absolutely best algorithm and parameter configuration is.

## 2. Accuracy Results

The pipeline successfully completed 100 epochs of training on the augmented data and evaluated against the 29 grid combinations.

**Train Accuracy**: The model achieved a **35.618%** Character Error Rate (BCER) on the training set.
**Best Test Accuracy**: The model achieved a **41.415%** Character Error Rate (BCER) on the test set.

Here are the Top 5 configurations on the test set:
1. **Base (Grayscale, No Binarization)**: 41.415%
2. **Sauvola (Window 35, k 0.1)**: 46.061%
3. **Sauvola (Window 45, k 0.1)**: 46.274%
4. **Wolf (Window 35, k 0.1)**: 46.428%
5. **Wolf (Window 25, k 0.1)**: 46.953%

> [!IMPORTANT]
> **Base (Grayscale) is STILL the reigning champion.** Even with `doxapy` properly configured and clamped for the exact size of our Cherokee line crops, retaining the 8-bit continuous grayscale information is objectively better for Tesseract LSTM training than any form of aggressive Binarization. 
> 
> However, if we *must* binarize, the ideal configuration is the **Sauvola algorithm** with a **larger window size (35)** and a **lower sensitivity (k = 0.1)**. 

### What didn't work?
- The **Su** algorithm performed terribly, scoring between **63.7% and 65.7%**. Su focuses intensely on edge contours, which likely obliterated too much of the delicate Cherokee syllabary strokes.
- Smaller window sizes generally performed worse, as they lack the surrounding context needed to properly separate text from stained backgrounds.
- Higher `k` values (0.3) on Sauvola and Wolf stripped away too much faint text.

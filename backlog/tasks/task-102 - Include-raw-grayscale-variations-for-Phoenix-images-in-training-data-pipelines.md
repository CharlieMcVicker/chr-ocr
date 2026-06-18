---
id: TASK-102
title: Include raw grayscale variations for Phoenix images in training data pipelines
status: To Do
assignee: []
created_date: '2026-06-18 02:33'
labels: []
dependencies: []
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add support for training on raw non-binarized grayscale images for the Cherokee Phoenix dataset. Currently, Phoenix images are exclusively binarized using Otsu, Su, Sauvola, or Wolf during training dataset generation and dynamic augmentation. Since evaluation shows grayscale (base) yields the lowest CER (4.680%), introducing raw grayscale variations into the training pipeline will align training data with the optimal evaluation format and improve model accuracy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Include 'grayscale' (native/unbinarized) as a training variation in scripts/augment_dataset.py for Phoenix scans
- [ ] #2 Add 'grayscale' (native/unbinarized) to the dynamic binarization selection pool in scripts/augment_dynamic.py for Phoenix scans
- [ ] #3 Verify that both static and dynamic training data generation scripts produce grayscale variations alongside binarized ones
<!-- AC:END -->

---
id: TASK-19
title: Fix and Finalize V2 Image Processing Pipeline
status: To Do
assignee: []
created_date: '2026-06-10 20:01'
updated_date: '2026-06-11 00:44'
labels:
  - backend
  - pipeline
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The next agent needs to execute the final fixes before launching the image pipeline. \n\n**Learnings & Context:**\n1. The `preview_bounding_boxes.py --overlay` script saves annotated images into the `scans/` directory as `.png` files. The extraction script currently grabs any `.jp2` or `.png` images it finds, which means it accidentally processed the annotated overlay images and baked the bounding boxes into the crops! We need to delete all `bbox_overlay_*.png` files in the `scans/` directory and update the `find_scans()` function in `prepare_training_data.py` to ignore them.\n2. Tesseract's connected-component line segmentation fails miserably on dense Cherokee text, merging multiple lines into a single bounding box. We need to revert line detection back to the Surya AI `DetectionPredictor` model in both `prepare_training_data.py` and `extract_lines.py`. Note that column grouping was successfully fixed in `server/layout.py`, so Surya will run on the correct, unified column crops.\n3. The current contents of `training_data_v2/` are polluted with bad multi-line crops and need to be deleted.\n4. A label reconsolidation script (`scripts/reconsolidate_labels.py`) was created that uses fuzzy text matching to seamlessly port old labels from the `v1` dataset onto the new `v2` dataset. There is also a backup of the v2 manifest at `training_data_v2_manifest_backup.json` in case the user labeled anything recently.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Delete all bbox_overlay_*.png files in scans/ directory
- [ ] #2 Wipe training_data_v2/ directory
- [ ] #3 Update find_scans() in prepare_training_data.py to ignore overlay files
- [ ] #4 Revert get_tesseract_line_bboxes to Surya DetectionPredictor in pipeline scripts
- [ ] #5 Launch prepare_training_data.py in the background
- [ ] #6 Run reconsolidate_labels.py after generation completes to port labels
- [ ] #7 Update crop_pad_normalize_line to support skipping normalization and returning high-res crop
- [ ] #8 Implement and formalize the Cherokee language filter heuristic (>= 5 characters) in prepare_training_data.py to skip English lines.
<!-- AC:END -->

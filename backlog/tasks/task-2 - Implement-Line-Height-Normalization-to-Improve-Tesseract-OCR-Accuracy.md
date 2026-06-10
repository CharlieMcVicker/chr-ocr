---
id: TASK-2
title: Implement Line-Height Normalization to Improve Tesseract OCR Accuracy
status: To Do
assignee: []
created_date: '2026-06-10 14:31'
updated_date: '2026-06-10 15:19'
labels: []
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Resize individual line crops extracted during preprocessing to a target height range of 30-33 pixels, while maintaining aspect ratio and applying specific scaling rules for artifacts, to align with Tesseract's preferred font size and improve transcription quality.
<!-- SECTION:DESCRIPTION:END -->


## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
**Implementation Plan for Line-Height Normalization (TASK-2)**

**Phase 1: Configuration & Setup**
1.  **Define TARGET_LINE_HEIGHT_RANGE:** Introduce a configuration parameter for `TARGET_LINE_HEIGHT_RANGE` (e.g., `[30, 33]`) in a relevant configuration file (e.g., `config.py` or a dedicated OCR pre-processing config).
2.  **Identify Line Crop Extraction Logic:** Locate the existing code responsible for extracting individual line crops from documents.

**Phase 2: Core Scaling Logic Development**
1.  **Implement Random Target Height Selection:** For each line crop, randomly select a `TARGET_LINE_HEIGHT` integer value within the configured `TARGET_LINE_HEIGHT_RANGE`.
2.  **Develop Scaling Function:** Create a utility function for scaling an image while preserving its aspect ratio. This function should accept an image and a target height.
    *   **Resampling Method:** Use a high-quality resampling algorithm (e.g., OpenCV's `cv2.INTER_LANCZOS4` or `cv2.INTER_CUBIC` for general good quality).
3.  **Implement Conditional Scaling Logic:**
    *   Get the original height of the line crop.
    *   If `original_height < 30` pixels: skip scaling.
    *   If `30 <= original_height <= 1.5 * selected_TARGET_LINE_HEIGHT`: skip scaling.
    *   If `original_height > 1.5 * selected_TARGET_LINE_HEIGHT`: apply the scaling function to reduce the image height to `selected_TARGET_LINE_HEIGHT`.

**Phase 3: Integration and Manifest Updates**
1.  **Integrate Scaling:** Apply the conditional scaling logic within the line crop extraction workflow.
2.  **Update `line_bbox` Coordinates:** After scaling, recalculate the `line_bbox` coordinates (width, height, x, y) in the document manifest to reflect the new dimensions of the scaled line image. Ensure x,y coordinates are adjusted proportionally to maintain relative positioning.

**Phase 4: Testing & Validation**
1.  **Unit Tests:** Write unit tests for the scaling function, covering all conditional scaling scenarios (no scale, scale down).
2.  **Integration Tests:** Test the end-to-end process with sample documents to ensure line crops are scaled correctly and OCR accuracy is maintained or improved.
3.  **Visual Inspection:** Visually inspect a sample of scaled line crops to confirm aspect ratio preservation and image quality.
4.  **OCR Performance Metrics:** Measure Tesseract OCR accuracy on a representative dataset before and after implementing line-height normalization.
<!-- SECTION:PLAN:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define a configurable TARGET_LINE_HEIGHT_RANGE (e.g., 30-33 pixels) and randomly select a TARGET_LINE_HEIGHT within this range for each line crop.
- [ ] #2 Update line crop extraction logic to resize images proportionally to the selected TARGET_LINE_HEIGHT using a high-quality resampling method (e.g., bicubic or Lanczos).
- [ ] #3 Ensure aspect ratio is strictly preserved during scaling.
- [ ] #4 Implement scaling logic: if original height < 30px, do not scale; if 30px <= original height <= 1.5 * TARGET_LINE_HEIGHT, do not scale; if original height > 1.5 * TARGET_LINE_HEIGHT, scale down to TARGET_LINE_HEIGHT with proportional jitter.
- [ ] #5 Update line_bbox coordinates in the manifest to match the new image dimensions if needed.
<!-- AC:END -->

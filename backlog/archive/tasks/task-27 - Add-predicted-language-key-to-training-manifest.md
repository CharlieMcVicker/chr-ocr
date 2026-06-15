---
id: TASK-27
title: Add predicted language key to training manifest
status: Done
assignee: []
created_date: '2026-06-11 02:24'
updated_date: '2026-06-11 02:52'
labels: []
dependencies: []
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the main image processing script finishes, update the manifest generation to run the Tesseract language classification and add a 'predicted_lang' key to each item in the manifest, rather than strictly filtering. This will aid the manual labeling process on the custom server.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update manifest generation to classify and add predicted_lang key
- [x] #2 Run classification against the complete new dataset
- [x] #3 Ensure custom server labeling UI utilizes predicted_lang
<!-- AC:END -->



## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
# Goal Description

The goal of this task (TASK-27) is to update the dataset manifest with language classifications (`predicted_lang`) using Tesseract models, which will aid the manual labeling process in the custom server UI. Since an expensive Computer Vision pipeline is currently running and writing to `training_data_v2/manifest.json`, we need a completely safe, read-only approach to avoid corrupting or locking this file.

## User Review Required

> [!IMPORTANT]
> The current CV script is actively writing to `training_data_v2/manifest.json`. To eliminate any risk of data corruption, we will **not** modify this file directly. Instead, we will create a standalone script that reads the current state of `manifest.json` and writes its enriched output to a completely separate file: `training_data_v2/manifest_w_lang.json`.
>
> Is this file naming (`manifest_w_lang.json`) acceptable? And should the server be updated to read from this new file once it's ready, or should we plan to manually replace `manifest.json` with it after the CV script officially finishes?

## Proposed Changes

---

### Scripts

#### [NEW] [scripts/add_predicted_lang_to_manifest.py](file:///Users/charlesmcvicker/code/phoenix/scripts/add_predicted_lang_to_manifest.py)
Create a new standalone python script that safely processes the manifest:
1. **Read-Only Input**: Load `training_data_v2/manifest.json` in a read-only manner.
2. **Incremental Processing**: Check if an output file `training_data_v2/manifest_w_lang.json` already exists. If so, load it to resume progress (this allows the script to process new entries added by the ongoing CV script if run multiple times).
3. **Classification**: For every item lacking a `predicted_lang` key:
   - Load the image crop (`item['image_path']`).
   - Run Tesseract OCR using both Cherokee and English models (`lang="chr+eng"`).
   - Pass the OCR result to `analyze_text` from `scripts.classify_layout`. This function already uses our recently computed ideal thresholds (English < 0.40, Cherokee > 0.45) to make the classification call based on the percentage of Cherokee characters vs Latin characters.
   - Assign the `"classification"` result to the `"predicted_lang"` key on the item.
4. **Safe Output**: Periodically (and at completion) save the updated dictionary to `training_data_v2/manifest_w_lang.json`. The original `manifest.json` is never written to.

---

### Server

#### [MODIFY] [server/app.py](file:///Users/charlesmcvicker/code/phoenix/server/app.py) (Optional / When Ready)
Once the CV pipeline is complete and the new manifest is generated, we will need to ensure the server UI utilizes this new manifest and displays the `predicted_lang`.
- Point the server's manifest path to `manifest_w_lang.json` (or wait for manual file rename).
- Update the labeling endpoint/UI context to pass `predicted_lang` to the frontend.

#### [MODIFY] Labeling UI (e.g. `server/templates/label.html` or equivalent)
- Update the UI to display the `predicted_lang` to assist the manual labeling process.

## Verification Plan

### Manual Verification
- Run the new script `python scripts/add_predicted_lang_to_manifest.py` while the CV script is running.
- Verify that `training_data_v2/manifest_w_lang.json` is created and populated with `predicted_lang` keys without throwing any locking/write errors on the main `manifest.json`.
- Start the server using the new manifest and visually confirm that the `predicted_lang` is visible in the labeling UI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation Details:\n1. Read the manifest created by 'prepare_training_data'\n2. Only process entries that lack a 'predicted_language' key (incremental processing)\n3. Classify those specific missing entries, and then write the file back atomicaly (e.g. write to a temporary file, then rename/move over the original) to ensure we don't corrupt the main manifest.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented scripts/add_predicted_lang_to_manifest.py to safely augment manifest.json into manifest_w_lang.json. Updated server/app.py and server/templates/training.html to read from manifest_w_lang.json and display predicted_lang natively in the UI.
<!-- SECTION:FINAL_SUMMARY:END -->

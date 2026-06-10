---
id: doc-4
title: Manifest Files Overview
type: other
created_date: '2026-06-10 19:19'
updated_date: '2026-06-10 19:19'
---
# Manifest Files Reference

There are two primary manifest files in this project:

## `uploads/manifest.json`
This file is NOT used for column splitting or training data extraction. It is managed by the web server to track raw image uploads from the UI. Each entry maps a UUID to the original filename and the upload timestamp.

## `training_data/manifest.json`
This is the core manifest for OCR training data. It tracks individual line crops extracted from scans, and contains the detailed metadata required for training, including `column_index`, `line_index`, bounding box coordinates, initial OCR text, and user labels.

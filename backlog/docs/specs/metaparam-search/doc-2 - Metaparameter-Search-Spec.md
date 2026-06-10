---
id: doc-2
title: Metaparameter Search Spec
type: specification
created_date: '2026-06-10 14:39'
updated_date: '2026-06-10 14:39'
---
# Metaparameter search

Using a small number of documents that have very different background and staining conditions, search config space of different algorithms and figure out which minimizes loss for these docs.

1. Find docs w different conditions
2. Transcribe for ground truth
3. Do some kind of parameter space search for each algorithm, optimize for accuracy on this small dataset.
   1. Keep all data for params/files, in case we want to add criteria to group scans later
4. Generate an html doc that lets me easily see the different algorithms and ground truth for the doc.
   1. Make it easy to "diff" the ground truth and algorithms from each other
5. Consider doing some kind of "model selection" based on some parameters calculated from the original image, eg. avg pixel value or smth.

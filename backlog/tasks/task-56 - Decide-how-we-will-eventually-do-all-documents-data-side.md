---
id: TASK-56
title: Decide how we will eventually do all documents (data side)
status: To Do
assignee: []
created_date: '2026-06-15 18:06'
updated_date: '2026-06-15 19:53'
labels: []
dependencies: []
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Establish the long-term data processing pipeline architecture for all documents. Decide whether to run columns -> lines -> tesseract, or run tesseract directly on columns or full documents. Evaluate skew/warp correction methods and document the chosen strategy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create an Architectural Decision Record (ADR) under backlog/decisions/ defining the document processing pipeline
- [ ] #2 Address page-level vs column-level vs line-level OCR options and trade-offs
- [ ] #3 Document the skew and warp correction strategy to be implemented
- [ ] #4 Obtain maintainer consensus on the final production data architecture
<!-- AC:END -->

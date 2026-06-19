# Cherokee Phoenix OCR

This repository contains the end-to-end pipeline, scripts, and web applications for processing and performing Optical Character Recognition (OCR) on the historic Cherokee Phoenix newspaper.

## Documentation Index

We maintain a structured documentation system designed to guide you through operations, reference systems, and project history.

### 📖 Operational Guides
*   **[Operations Guide](./backlog/docs/guides/ocr-operations/doc-13%20-%20Cherokee-OCR-Operations-Guide.md)**: The master manual for the Cherokee Phoenix OCR project. Details end-to-end workflows from raw page scans to model deployment.
*   **[Active Learning & Labeling](./backlog/docs/guides/active-learning-labeling.md)**: Playbook for human-in-the-loop manual labeling, web endpoints, and template architectures.
*   **[Cherokee New Testament (CNT) Integration](./backlog/docs/guides/cnt-integration.md)**: Reference for dynamic programming alignments, hyphenation heuristics, and multi-source corpus mixing.
*   **[Text Normalization & Unicharset Guide](./backlog/docs/guides/normalization-unicharset.md)**: Technical specifications for standardizing text, compiling `traineddata`, and rare character class balancing.
*   **[Local Model Rebuild Runbook](./backlog/docs/guides/doc-12%20-%20How-to-Rebuild-Local-Model-and-Regenerate-FTM-Predictions.md)**: Concise runbook on rebuilding local models and regenerating labeling interface predictions.

### 📐 Technical References
*   **[Mixed Training & Augmentation Spec](./backlog/docs/reference/mixed-training-augmentation.md)**: Operational specification for stable seeded sampling, elastic distortions, ink smudge models, and noise injection.
*   **[Sweeps & Validation Architecture](./backlog/docs/reference/sweeps-evaluation.md)**: Architecture, config structures, and metrics execution rules for automated training sweeps.
*   **[Grayscale & Binarization Optimization](./backlog/docs/reference/binarization-grayscale-optimization.md)**: Deep mathematical and empirical evaluation of image preprocessing, thresholding algorithms, and DP ensemble voting.

### 🤖 AI Agent Systems
*   **[AI Agents Guide](./agents.md)**: Standard protocols, tools (Ember, Backlog CLI), and behavioral rules for AI assistants collaborating on this codebase.

### 🗄️ Historical Archive
*   All older specifications, training run trackers, completed migration plans, and specific evaluation metrics from past iterations are isolated in the **[Historical Archive](./backlog/docs/archive/)** to ensure our contemporary workflow resources remain clear and focused.

---

## System Setup & Dependencies

Before running the scripts or server, ensure you have the following system packages installed:

```bash
# macOS (using Homebrew)
brew install imagemagick
brew install tesseract
brew install llama.cpp

# Python Setup
uv sync
```

- Ensure the Cherokee training data file `chr.traineddata` (available from [Tesseract OCR Tessdata Repository](https://github.com/tesseract-ocr/tessdata/blob/main/chr.traineddata)) is placed in your system's `tessdata` directory.

---

## Codebase Modular Structure

The codebase is structured as a modular Python package (`phoenix/`) with thin scripts and server endpoints importing reusable core logic from it:

- **`phoenix.config`**: Defines dataclasses for training parameters and hyperparameter sweep setups (`TrainingConfig`, `SweepConfig`).
- **`phoenix.manifest`**: Manages manifest dataset load/save operations, splits (train/test), cleanups, label reconsolidation, and line crop operations.
- **`phoenix.training`**: Holds ML pipeline orchestration (staged epoch loop, checkpoint sweep evaluation) and data augmentation (elastic transforms, ink simulation, mixup).
- **`phoenix.layout`**: Segment scans into columns/lines (via Surya), classifies column/line layout languages, and performs PyTesseract FTM prediction enrichment.

---

## Web OCR Server & Dashboard
 
The web app provides a visual UI to upload document images, preprocess them using multiple binarization algorithms (Textcleaner, Doxa - Su, Doxa - Sauvola, and Doxa - Wolf), run Tesseract OCR on each version, and compare/view the results in an interactive tabbed hOCR overlay viewer.

### Setup and Running Local Server

1. **Setup and Synchronize Virtual Environment**:
   ```zsh
   uv sync
   ```

2. **Start the Flask Server**:
   ```zsh
   PORT=5001 uv run python server/app.py
   ```

4. Open your browser and go to: `http://localhost:5001`

### Configuration

You can customize the server by setting environment variables or creating a `.env` file:
- `PORT`: Server port (default: `5000`)
- `UPLOAD_DIR`: Path where uploads and results are stored (default: `<project-root>/uploads`)

---

## Docker Setup & Requirements

If you want to containerize this application, here is a brief overview of how and where to install the required system libraries, language data, and Python dependencies:

### 1. Base Image and System Libraries
Use a Python base image (such as `python:3.11-slim`) and install `tesseract-ocr` and `imagemagick` via `apt`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    imagemagick \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### 2. Cherokee Language Data (`chr.traineddata`)
Tesseract needs the `chr.traineddata` file to perform Cherokee OCR. Download it and place it into the `tessdata` folder of the image. For standard Debian-based slim images, this path is typically `/usr/share/tesseract-ocr/5/tessdata/` (or `/usr/share/tesseract-ocr/4.00/tessdata/` depending on the Tesseract version):
```dockerfile
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata/ \
    && curl -L -o /usr/share/tesseract-ocr/5/tessdata/chr.traineddata \
    https://github.com/tesseract-ocr/tessdata/raw/main/chr.traineddata
```

### 3. Application Dependencies & Run
Copy the application source code, install Python packages, and set up the startup command:
```dockerfile
WORKDIR /app
COPY server/requirements.txt ./server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

COPY . .

ENV PORT=5001
EXPOSE 5001

CMD ["python", "server/app.py"]
```

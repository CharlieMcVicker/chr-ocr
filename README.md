# Cherokee Phoenix OCR

This repository contains the end-to-end pipeline, scripts, and web applications for processing and performing Optical Character Recognition (OCR) on the historic Cherokee Phoenix newspaper.

## Documentation Index

We have a comprehensive documentation system to help you navigate the codebase, understand the ML pipeline, and collaborate with AI agents.

- **[Operations Guide](./backlog/docs/guides/ocr-operations/doc-13%20-%20Cherokee-OCR-Operations-Guide.md)**: The master manual for the Cherokee Phoenix OCR project. It details the workflow from processing raw page scans to fine-tuning the Tesseract LSTM model, managing annotations, and deploying the model for inference in the labeling interface.
- **[AI Agents Guide](./agents.md)**: Instructions and context on how AI agents (like Antigravity) are integrated into this project, including how they use the Backlog CLI and Semantic Search.
- **Backlog Docs**: Detailed research notes, experiments, and technical specs are maintained in the `backlog/docs/` directory. Use the `backlog` CLI to search for specific topics.

---

## System Setup & Dependencies

Before running the scripts or server, ensure you have the following system packages installed:

```bash
# macOS (using Homebrew)
brew install imagemagick
brew install tesseract
brew install llama.cpp

# Python Dependencies
pip install surya-ocr pillow numpy scipy
```

- Ensure the Cherokee training data file `chr.traineddata` (available from [Tesseract OCR Tessdata Repository](https://github.com/tesseract-ocr/tessdata/blob/main/chr.traineddata)) is placed in your system's `tessdata` directory.

---

## Web OCR Server & Dashboard
 
The web app provides a visual UI to upload document images, preprocess them using multiple binarization algorithms (Textcleaner, Doxa - Su, Doxa - Sauvola, and Doxa - Wolf), run Tesseract OCR on each version, and compare/view the results in an interactive tabbed hOCR overlay viewer.

### Setup and Running Local Server

1. **Create and Activate Virtual Environment**:
   ```zsh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install Dependencies**:
   ```zsh
   pip install -r server/requirements.txt
   ```

3. **Start the Flask Server**:
   ```zsh
   PORT=5001 python server/app.py
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

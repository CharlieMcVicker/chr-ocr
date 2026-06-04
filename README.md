# Scripts for doing OCR (text recognition) on the Cherokee Phoenix

This repository contains CLI scripts and a full Flask web application for processing and viewing OCR results of Cherokee document images.

## System Dependencies

Before running the scripts or server, ensure you have the following system packages installed:

- `imagemagick`
- `tesseract`
- Ensure the Cherokee training data file `chr.traineddata` (available from [Tesseract OCR Tessdata Repository](https://github.com/tesseract-ocr/tessdata/blob/main/chr.traineddata)) is placed in your system's `tessdata` directory.

---

## 1. Web OCR Server & Dashboard

The web app provides a visual UI to upload PNG files, clean them automatically, perform OCR, and view the results in an interactive overlay.

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

## 2. CLI Scripts

You can also run image processing and OCR directly from your terminal.

### Clean an image file

```zsh
./scripts/clean-img ./path/to/image.png
ls ./path/to/image.png-out.png
```

### Run OCR on an image file

```zsh
./scripts/call-tesseract ./path/to/image.png-out.png
```

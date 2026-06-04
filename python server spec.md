# Python Server for Cherokee OCR

A simple Flask server for doing OCR on Cherokee documents. Users upload a PNG,
the server cleans and OCRs it server-side, and the result is shown via the
hOCR viewer on a dedicated results page.

---

## Stack

- **Framework**: Flask
- **Language**: Python 3
- **OCR pipeline**: existing shell scripts (`scripts/clean-img` + `scripts/call-tesseract`)
- **Storage**: local filesystem (`uploads/` directory next to the server)
- **Persistence**: JSON manifest on disk (`uploads/manifest.json`)

---

## Core Workflow

1. User visits the home page and drops/selects a PNG file.
2. Server receives the upload over HTTP.
3. Server **downscales** the image to a max of 2400px on the longest side (using ImageMagick).
4. Server runs `scripts/clean-img` on the downscaled PNG.
5. Server runs `scripts/call-tesseract` (with `-l chr --dpi 300 hocr`) on the cleaned PNG.
6. Server assigns the upload a **random UUID**, saves the cleaned PNG and hOCR output under `uploads/<uuid>/`.
7. Server records an entry in `uploads/manifest.json`:
   - `id` (UUID)
   - `original_filename` (user's uploaded filename)
   - `uploaded_at` (ISO 8601 timestamp)
8. Server **redirects** the user to `/view/<id>`.
9. The `/view/<id>` page serves the hOCR file with `Content-Type: text/html` and injects the hOCR.js viewer script so the result is rendered in-browser.

---

## API / Routes

| Method | Route            | Description                                              |
|--------|------------------|----------------------------------------------------------|
| GET    | `/`              | Home page — upload form + bank of previously uploaded images |
| POST   | `/upload`        | Accepts PNG, runs pipeline, redirects to `/view/<id>`    |
| GET    | `/view/<id>`     | hOCR viewer page for the given upload                    |
| GET    | `/uploads/<id>/cleaned.png` | Serve the cleaned PNG (for thumbnail/preview)  |
| GET    | `/uploads/<id>/out.html`    | Raw hOCR HTML (served as `text/html`, not XML) |

---

## File Storage Layout

```
uploads/
  manifest.json          # array of { id, original_filename, uploaded_at }
  <uuid>/
    original.png         # downscaled original upload
    cleaned.png          # output of clean-img
    out.html             # hOCR output (renamed from tesseract's .hocr)
```

---

## Home Page — Image Bank

The home page shows:
- A **drag-and-drop upload area** (also has a file picker fallback).
- A **thumbnail grid** of all previously uploaded images (from the manifest), each linking to its `/view/<id>` page.
- Below the grid, a **text list** of the same uploads showing original filename and upload date.

---

## Image Processing Rules

- **File type**: PNG only; return HTTP 400 for other types.
- **Downscaling**: Always resize so the longest side ≤ 2400px before cleaning (using ImageMagick `convert -resize 2400x2400>`).
- **No hard file-size cap** on the server; rely on downscaling to keep things manageable.

---

## Deployment

- Open access — no authentication required.
- Designed for local development (`localhost`) and simple self-hosted use.
- Port and upload directory should be configurable via environment variables (`PORT`, `UPLOAD_DIR`).

---

## Dependencies

- `flask`
- `imagemagick` (system)
- `tesseract` + `chr.traineddata` (system)
- hOCR.js viewer script (injected client-side)

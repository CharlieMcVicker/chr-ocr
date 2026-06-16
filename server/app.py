"""
Flask web application for the Cherokee OCR project.

This application provides the main web-based interface, supporting:
- Multi-algorithm file uploads and processing (original, clean, Doxa binarizations).
- Real-time page rendering of processed documents, including hOCR viewers.
- Interactive training data labeling editor and performance stats tracker.
- Manifest loading and saving handlers.
"""

from server.process_file import process_file
import os
import uuid
import json
from datetime import datetime, timezone
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_from_directory,
    abort,
    make_response,
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Resolve absolute paths dynamically relative to this file location
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SERVER_DIR)

# Configurations
UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(PROJECT_ROOT, "uploads"))
PORT = int(os.getenv("PORT", 5000))

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
MANIFEST_PATH = os.path.join(UPLOAD_DIR, "manifest.json")
if not os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, "w") as f:
        json.dump([], f)

TRAINING_DIR = os.path.join(PROJECT_ROOT, "training_data")
TRAINING_MANIFEST_PATH = os.path.join(TRAINING_DIR, "manifest_w_lang.json")


def load_manifest():
    """
    Loads the uploaded files manifest JSON database.

    Returns:
        list: A list of dict metadata objects for all uploads, or an empty list on failure.
    """
    try:
        with open(MANIFEST_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []


def load_training_manifest():
    """
    Loads the training data manifest database tracking Cherokee text lines and annotations.

    Returns:
        dict: The mapped dataset dict, or an empty dictionary if file does not exist or fails to load.
    """
    if not os.path.exists(TRAINING_MANIFEST_PATH):
        return {}
    try:
        with open(TRAINING_MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_training_manifest(manifest):
    """
    Saves/serializes the training data manifest back to disk.

    Args:
        manifest (dict): The dataset dictionary to serialize.
    """
    with open(TRAINING_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def save_manifest(manifest):
    """
    Saves/serializes the uploads manifest back to disk.

    Args:
        manifest (list): The list of upload metadata objects to serialize.
    """
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


@app.route("/")
def index():
    """
    Renders the dashboard/homepage containing historical uploaded scans, sorted
    reverse-chronologically.

    Returns:
        str: Rendered HTML template response.
    """
    manifest = load_manifest()
    # Sort manifest reverse-chronologically (newest first)
    manifest_sorted = sorted(
        manifest, key=lambda x: x.get("uploaded_at", ""), reverse=True
    )
    return render_template("index.html", uploads=manifest_sorted)


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Handles user image uploads. Registers the image, generates directories,
    invokes the processing pipeline asynchronously or synchronously, updates
    the manifest database, and redirects the user to the results.

    Returns:
        Response: HTTP redirect to view results, or 400 Bad Request error string.
    """
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".tif", ".bmp"}
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        return f"Only {', '.join(sorted(ALLOWED_EXTENSIONS))} files are allowed", 400

    # Generate UUID and create directories
    file_id = str(uuid.uuid4())
    item_dir = os.path.join(UPLOAD_DIR, file_id)
    os.makedirs(item_dir, exist_ok=True)

    # Save original uploaded file with its original extension
    original_uploaded_path = os.path.join(item_dir, f"original{ext}")
    file.save(original_uploaded_path)

    err = process_file(original_uploaded_path, project_root=PROJECT_ROOT, file_id=file_id)
    if err:
        return err

    # Save to manifest
    manifest = load_manifest()
    manifest.append(
        {
            "id": file_id,
            "original_filename": file.filename,
            "uploaded_at": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
        }
    )
    save_manifest(manifest)

    return redirect(url_for("view_result", file_id=file_id))


@app.route("/view/<file_id>")
def view_result(file_id):
    """
    Renders the detailed multi-algorithm output page for a single processed upload.

    Args:
        file_id (str): The unique identifier of the uploaded scan.

    Returns:
        str: Rendered HTML page or 404 error response.
    """
    manifest = load_manifest()
    item = next((x for x in manifest if x["id"] == file_id), None)
    if not item:
        abort(404)
    return render_template("view.html", item=item)


@app.route("/uploads/<file_id>/<filename>")
def serve_upload_file(file_id, filename):
    """
    Serves static assets and processed files (including images and interactive hOCR documents)
    from the uploads directories. Automatically injects hocr.js scripts to HTML files.

    Args:
        file_id (str): The unique identifier of the upload folder.
        filename (str): The specific file name within that directory.

    Returns:
        Response: The file content response with correct headers, or 404 error.
    """
    allowed_files = {
        "cleaned.png",
        "original.png",
        "cleaned.html",
        "original.html",
        "out.html",
        "doxa_su.png",
        "doxa_sauvola.png",
        "doxa_wolf.png",
        "doxa_su.html",
        "doxa_sauvola.html",
        "doxa_wolf.html",
    }
    if filename not in allowed_files:
        abort(404)

    file_path = os.path.join(UPLOAD_DIR, file_id, filename)
    # Support backward compatibility for out.html
    if filename == "out.html" and not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, file_id, "cleaned.html")

    if not os.path.exists(file_path):
        abort(404)

    if filename.endswith(".html"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Inject hocr.js viewer script if it isn't already there
        if "hocrjs" not in content:
            script_tag = '\n<script defer src="https://unpkg.com/hocrjs"></script>\n'
            if "</body>" in content:
                content = content.replace("</body>", f"{script_tag}</body>")
            else:
                content += script_tag

        response = make_response(content)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response
    else:
        return send_from_directory(os.path.join(UPLOAD_DIR, file_id), filename)


@app.route("/training_data/<path:filename>")
def serve_training_data(filename):
    """
    Serves raw static image line crops and training assets from the V2 training directory.

    Args:
        filename (str): Path of the file relative to training directory.

    Returns:
        Response: The requested static file.
    """
    return send_from_directory(TRAINING_DIR, filename)


@app.route("/training")
def training_editor():
    """
    Renders the web-based interactive dataset annotator and classifier review dashboard.
    Performs on-the-fly layout and text pattern classification for unlabeled elements.

    Returns:
        str: Rendered training UI editor.
    """
    from phoenix.layout import analyze_text
    manifest = load_training_manifest()
    
    # Return manifest as list of items for easier frontend handling
    items = []
    for item in manifest.values():
        if "classification" not in item:
            # Analyze initial_ocr or label to get the classification
            txt = item.get("label") or item.get("initial_ocr", "")
            item["classification"] = analyze_text(txt)["classification"]
        items.append(item)
    
    # Calculate stats
    total = len(items)
    unlabeled = sum(1 for x in items if x.get("status") == "unlabeled")
    labeled = sum(1 for x in items if x.get("status") == "labeled")
    not_cherokee = sum(1 for x in items if x.get("status") == "not_cherokee")
    nasty_crop = sum(1 for x in items if x.get("status") == "nasty_crop")
    
    stats = {
        "total": total,
        "unlabeled": unlabeled,
        "labeled": labeled,
        "not_cherokee": not_cherokee,
        "nasty_crop": nasty_crop
    }
    
    return render_template("training.html", items=items, stats=stats)


@app.route("/training/update", methods=["POST"])
def update_training_item():
    """
    Receives JSON POST updates modifying training line annotations or review states,
    saving changes directly to the training manifest.

    Returns:
        dict: Success dictionary on completion, or error dictionary with 400/404 HTTP codes.
    """
    data = request.json
    if not data or "id" not in data:
        return {"error": "Missing item ID"}, 400
        
    item_id = data["id"]
    status = data.get("status")
    label = data.get("label")
    
    manifest = load_training_manifest()
    if item_id not in manifest:
        return {"error": "Item not found in training data manifest"}, 404
        
    if status is not None:
        manifest[item_id]["status"] = status
    if label is not None:
        manifest[item_id]["label"] = label
        
    save_training_manifest(manifest)
    return {"success": True}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

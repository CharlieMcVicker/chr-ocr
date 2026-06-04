import os
import uuid
import json
import subprocess
from datetime import datetime, timezone
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, abort, make_response
from dotenv import load_dotenv
from binarizer import binarize_image

load_dotenv()

app = Flask(__name__)

# Resolve absolute paths dynamically relative to this file location
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SERVER_DIR)

# Configurations
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(PROJECT_ROOT, 'uploads'))
PORT = int(os.getenv('PORT', 5000))

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
MANIFEST_PATH = os.path.join(UPLOAD_DIR, 'manifest.json')
if not os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, 'w') as f:
        json.dump([], f)

def load_manifest():
    try:
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_manifest(manifest):
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

@app.route('/')
def index():
    manifest = load_manifest()
    # Sort manifest reverse-chronologically (newest first)
    manifest_sorted = sorted(manifest, key=lambda x: x.get('uploaded_at', ''), reverse=True)
    return render_template('index.html', uploads=manifest_sorted)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.tiff', '.tif', '.bmp'}
    filename = file.filename.lower()
    ext = os.path.splitext(filename)[1]
    if ext not in ALLOWED_EXTENSIONS:
        return f"Only {', '.join(sorted(ALLOWED_EXTENSIONS))} files are allowed", 400

    # Generate UUID and create directories
    file_id = str(uuid.uuid4())
    item_dir = os.path.join(UPLOAD_DIR, file_id)
    os.makedirs(item_dir, exist_ok=True)

    # Save original uploaded file with its original extension
    original_uploaded_path = os.path.join(item_dir, f'original{ext}')
    file.save(original_uploaded_path)

    # Resolve executable scripts absolute paths
    clean_script_path = os.path.join(PROJECT_ROOT, 'scripts', 'clean-img')
    tesseract_script_path = os.path.join(PROJECT_ROOT, 'scripts', 'call-tesseract')

    original_path = os.path.join(item_dir, 'original.png')

    # Transcode and downscale to max 2400px on longest side using ImageMagick
    try:
        subprocess.run(
            ['magick', 'convert', original_uploaded_path, '-resize', '2400x2400>', original_path],
            check=True
        )
    except Exception as e:
        # Fallback to convert
        try:
            subprocess.run(
                ['convert', original_uploaded_path, '-resize', '2400x2400>', original_path],
                check=True
            )
        except Exception as e2:
            return f"Image transcode/resize failed: {str(e2)}", 500

    # Clean up original uploaded file if it was transcoded (i.e. not already .png)
    if ext != '.png':
        try:
            os.remove(original_uploaded_path)
        except Exception:
            pass

    # 2. Run clean script (creates original.png-out.png, original.png-tmp.png, etc.)
    # Note: clean-img expects to be run with project root as working directory to find textcleaner.
    original_path_rel = os.path.relpath(original_path, PROJECT_ROOT)
    try:
        subprocess.run(
            [clean_script_path, original_path_rel],
            cwd=PROJECT_ROOT,
            check=True
        )
    except Exception as e:
        return f"Image cleaning failed: {str(e)}", 500

    cleaned_out_path = original_path + '-out.png'
    cleaned_path = os.path.join(item_dir, 'cleaned.png')

    if os.path.exists(cleaned_out_path):
        os.rename(cleaned_out_path, cleaned_path)
    else:
        return "Cleaned image not found after running script", 500

    # Clean up temp files from clean-img script
    for tmp_suffix in ['-tmp.png', '-tmp2.png', '-tmp3.png']:
        tmp_file = original_path + tmp_suffix
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass

    # 2.5 Run Doxa binarization algorithms (Su, Sauvola, Wolf)
    doxa_algos = ['su', 'sauvola', 'wolf']
    for algo in doxa_algos:
        doxa_png_path = os.path.join(item_dir, f'doxa_{algo}.png')
        try:
            binarize_image(original_path, doxa_png_path, algo)
        except Exception as e:
            return f"Doxa binarization ({algo}) failed: {str(e)}", 500

    # 3. Run tesseract on cleaned.png
    out_uploads_item_dir = os.path.join(PROJECT_ROOT, 'out-uploads', file_id)
    os.makedirs(out_uploads_item_dir, exist_ok=True)

    cleaned_path_rel = os.path.relpath(cleaned_path, PROJECT_ROOT)
    try:
        subprocess.run(
            [tesseract_script_path, cleaned_path_rel],
            cwd=PROJECT_ROOT,
            check=True
        )
    except Exception as e:
        return f"OCR processing on cleaned image failed: {str(e)}", 500

    # Locate and copy/rename the resulting .hocr file (stored as cleaned.html)
    tesseract_output_cleaned = os.path.join(out_uploads_item_dir, 'cleaned.png.hocr')
    if not os.path.exists(tesseract_output_cleaned):
        tesseract_output_cleaned_alt = os.path.join(out_uploads_item_dir, 'cleaned.hocr')
        if os.path.exists(tesseract_output_cleaned_alt):
            tesseract_output_cleaned = tesseract_output_cleaned_alt

    dest_cleaned_hocr_path = os.path.join(item_dir, 'cleaned.html')
    if os.path.exists(tesseract_output_cleaned):
        # Read content and rewrite the image title path to just "cleaned.png"
        with open(tesseract_output_cleaned, 'r', encoding='utf-8') as f:
            hocr_content = f.read()
        
        import re
        hocr_content = re.sub(r'image\s+"[^"]+"', 'image "cleaned.png"', hocr_content)
        
        with open(dest_cleaned_hocr_path, 'w', encoding='utf-8') as f:
            f.write(hocr_content)
    else:
        return "hOCR output file for cleaned image not found", 500

    # 4. Run tesseract on original.png
    original_path_rel = os.path.relpath(original_path, PROJECT_ROOT)
    try:
        subprocess.run(
            [tesseract_script_path, original_path_rel],
            cwd=PROJECT_ROOT,
            check=True
        )
    except Exception as e:
        return f"OCR processing on original image failed: {str(e)}", 500

    tesseract_output_original = os.path.join(out_uploads_item_dir, 'original.png.hocr')
    if not os.path.exists(tesseract_output_original):
        tesseract_output_original_alt = os.path.join(out_uploads_item_dir, 'original.hocr')
        if os.path.exists(tesseract_output_original_alt):
            tesseract_output_original = tesseract_output_original_alt

    dest_original_hocr_path = os.path.join(item_dir, 'original.html')
    if os.path.exists(tesseract_output_original):
        # Read content and rewrite the image title path to just "original.png"
        with open(tesseract_output_original, 'r', encoding='utf-8') as f:
            hocr_content = f.read()
        
        import re
        hocr_content = re.sub(r'image\s+"[^"]+"', 'image "original.png"', hocr_content)
        
        with open(dest_original_hocr_path, 'w', encoding='utf-8') as f:
            f.write(hocr_content)
    else:
        return "hOCR output file for original image not found", 500

    # 5. Run tesseract on Doxa images
    for algo in doxa_algos:
        doxa_png_path = os.path.join(item_dir, f'doxa_{algo}.png')
        doxa_png_path_rel = os.path.relpath(doxa_png_path, PROJECT_ROOT)
        try:
            subprocess.run(
                [tesseract_script_path, doxa_png_path_rel],
                cwd=PROJECT_ROOT,
                check=True
            )
        except Exception as e:
            return f"OCR processing on Doxa {algo} image failed: {str(e)}", 500

        tesseract_output_doxa = os.path.join(out_uploads_item_dir, f'doxa_{algo}.png.hocr')
        if not os.path.exists(tesseract_output_doxa):
            tesseract_output_doxa_alt = os.path.join(out_uploads_item_dir, f'doxa_{algo}.hocr')
            if os.path.exists(tesseract_output_doxa_alt):
                tesseract_output_doxa = tesseract_output_doxa_alt

        dest_doxa_hocr_path = os.path.join(item_dir, f'doxa_{algo}.html')
        if os.path.exists(tesseract_output_doxa):
            with open(tesseract_output_doxa, 'r', encoding='utf-8') as f:
                hocr_content = f.read()
            
            import re
            hocr_content = re.sub(r'image\s+"[^"]+"', f'image "doxa_{algo}.png"', hocr_content)
            
            with open(dest_doxa_hocr_path, 'w', encoding='utf-8') as f:
                f.write(hocr_content)
        else:
            return f"hOCR output file for Doxa {algo} image not found", 500

    # Clean up out-uploads structure
    try:
        if os.path.exists(out_uploads_item_dir):
            import shutil
            shutil.rmtree(out_uploads_item_dir)
        parent_out = os.path.join(PROJECT_ROOT, 'out-uploads')
        if os.path.exists(parent_out) and not os.listdir(parent_out):
            os.rmdir(parent_out)
    except Exception:
        pass

    # Save to manifest
    manifest = load_manifest()
    manifest.append({
        'id': file_id,
        'original_filename': file.filename,
        'uploaded_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    })
    save_manifest(manifest)

    return redirect(url_for('view_result', file_id=file_id))

@app.route('/view/<file_id>')
def view_result(file_id):
    manifest = load_manifest()
    item = next((x for x in manifest if x['id'] == file_id), None)
    if not item:
        abort(404)
    return render_template('view.html', item=item)

@app.route('/uploads/<file_id>/<filename>')
def serve_upload_file(file_id, filename):
    allowed_files = {
        'cleaned.png', 'original.png', 'cleaned.html', 'original.html', 'out.html',
        'doxa_su.png', 'doxa_sauvola.png', 'doxa_wolf.png',
        'doxa_su.html', 'doxa_sauvola.html', 'doxa_wolf.html'
    }
    if filename not in allowed_files:
        abort(404)

    file_path = os.path.join(UPLOAD_DIR, file_id, filename)
    # Support backward compatibility for out.html
    if filename == 'out.html' and not os.path.exists(file_path):
        file_path = os.path.join(UPLOAD_DIR, file_id, 'cleaned.html')

    if not os.path.exists(file_path):
        abort(404)

    if filename.endswith('.html'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Inject hocr.js viewer script if it isn't already there
        if 'hocrjs' not in content:
            script_tag = '\n<script defer src="https://unpkg.com/hocrjs"></script>\n'
            if '</body>' in content:
                content = content.replace('</body>', f'{script_tag}</body>')
            else:
                content += script_tag

        response = make_response(content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    else:
        return send_from_directory(os.path.join(UPLOAD_DIR, file_id), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)

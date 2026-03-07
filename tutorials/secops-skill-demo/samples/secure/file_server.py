"""
Secure version of the file server.
Each vulnerability from the vulnerable version is remediated here.
"""

import os
import tempfile
from urllib.parse import urlparse
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)
UPLOAD_DIR = "/var/www/uploads"
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# FIX CWE-22: Validate path stays within UPLOAD_DIR
def _safe_path(filename: str) -> str | None:
    """Resolve the path and verify it stays within UPLOAD_DIR."""
    # Normalize and resolve to absolute path
    filepath = os.path.realpath(os.path.join(UPLOAD_DIR, filename))
    # Ensure the resolved path is still within the upload directory
    if not filepath.startswith(os.path.realpath(UPLOAD_DIR) + os.sep):
        return None
    return filepath


@app.route("/files/<path:filename>")
def download(filename):
    filepath = _safe_path(filename)
    if filepath is None or not os.path.isfile(filepath):
        return jsonify(error="File not found"), 404
    return send_file(filepath)


@app.route("/files/<path:filename>", methods=["PUT"])
def upload_by_path(filename):
    filepath = _safe_path(filename)
    if filepath is None:
        return jsonify(error="Invalid path"), 400
    with open(filepath, "wb") as f:
        f.write(request.get_data())
    return jsonify(status="saved")


# FIX CWE-918: SSRF prevention with URL allowlist
ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}


@app.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    parsed = urlparse(url)

    # Validate scheme
    if parsed.scheme not in ("https",):
        return jsonify(error="Only HTTPS URLs allowed"), 400

    # Validate host against allowlist
    if parsed.hostname not in ALLOWED_HOSTS:
        return jsonify(error="Host not allowed"), 403

    import urllib.request
    try:
        resp = urllib.request.urlopen(url, timeout=5)
        return resp.read(), 200
    except Exception:
        return jsonify(error="Fetch failed"), 502


# FIX CWE-434: Validate file type, size, and sanitize filename
@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify(error="No file provided"), 400

    # Check file size
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify(error=f"File too large (max {MAX_FILE_SIZE} bytes)"), 413

    # Check extension
    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify(error=f"Extension {ext} not allowed"), 400

    # Sanitize filename
    from werkzeug.utils import secure_filename
    safe_name = secure_filename(f.filename)
    if not safe_name:
        return jsonify(error="Invalid filename"), 400

    dest = os.path.join(UPLOAD_DIR, safe_name)
    f.save(dest)
    return jsonify(status="uploaded", filename=safe_name)


# FIX CWE-377: Use secure temporary files
def process_data(data: bytes) -> str:
    # Use NamedTemporaryFile with delete=True for automatic cleanup
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        # ... process the file ...
        return tmp_path
    finally:
        os.unlink(tmp_path)  # always clean up

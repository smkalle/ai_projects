"""
Intentionally vulnerable file server.
DO NOT deploy this code — it exists solely for security audit training.

Vulnerability classes demonstrated:
  - CWE-22:  Path Traversal
  - CWE-918: Server-Side Request Forgery (SSRF)
  - CWE-434: Unrestricted File Upload
  - CWE-377: Insecure Temporary File
"""

import os
import tempfile
import urllib.request
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)
UPLOAD_DIR = "/var/www/uploads"


# -- CWE-22: Path Traversal (read) ---------------------------------------
@app.route("/files/<path:filename>")
def download(filename):
    # VULNERABLE: no path normalization — ../../etc/passwd works
    filepath = os.path.join(UPLOAD_DIR, filename)
    return send_file(filepath)


# -- CWE-22: Path Traversal (write) --------------------------------------
@app.route("/files/<path:filename>", methods=["PUT"])
def upload_by_path(filename):
    # VULNERABLE: attacker controls destination path
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(request.get_data())
    return jsonify(status="saved", path=filepath)


# -- CWE-918: Server-Side Request Forgery --------------------------------
@app.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    # VULNERABLE: no allowlist — attacker can reach internal services
    # e.g., ?url=http://169.254.169.254/latest/meta-data/
    try:
        resp = urllib.request.urlopen(url)
        return resp.read(), 200
    except Exception as e:
        return jsonify(error=str(e)), 400


# -- CWE-434: Unrestricted File Upload -----------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return jsonify(error="no file"), 400

    # VULNERABLE: no extension or MIME type check — .php, .sh, .exe all accepted
    # VULNERABLE: original filename used directly — could overwrite system files
    dest = os.path.join(UPLOAD_DIR, f.filename)
    f.save(dest)
    return jsonify(status="uploaded", filename=f.filename)


# -- CWE-377: Insecure Temporary File ------------------------------------
def process_data(data: bytes) -> str:
    # VULNERABLE: predictable temp file, world-readable, not cleaned up
    tmp = tempfile.mktemp(suffix=".dat")  # mktemp is insecure
    with open(tmp, "wb") as f:
        f.write(data)

    # ... process the file ...
    return tmp  # temp file never deleted

"""
Intentionally vulnerable data handling module.
DO NOT deploy this code — it exists solely for security audit training.

Vulnerability classes demonstrated:
  - CWE-502: Deserialization of Untrusted Data
  - CWE-95:  Improper Neutralization of Directives in Dynamically Evaluated Code
  - CWE-611: Improper Restriction of XML External Entity Reference
  - CWE-117: Improper Output Neutralization for Logs
"""

import json
import pickle
import logging
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify

app = Flask(__name__)
logger = logging.getLogger(__name__)


# -- CWE-502: Insecure Deserialization -----------------------------------
@app.route("/import", methods=["POST"])
def import_data():
    raw = request.get_data()
    fmt = request.args.get("format", "json")

    if fmt == "pickle":
        # VULNERABLE: arbitrary code execution via crafted pickle payload
        data = pickle.loads(raw)
    elif fmt == "json":
        data = json.loads(raw)
    else:
        return jsonify(error="unsupported format"), 400

    return jsonify(imported=len(data) if isinstance(data, list) else 1)


# -- CWE-95: Code Injection via eval() -----------------------------------
@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.json.get("expression", "0")
    # VULNERABLE: arbitrary Python code execution
    try:
        result = eval(expression)
        return jsonify(result=result)
    except Exception as e:
        return jsonify(error=str(e)), 400


# -- CWE-95: Code Injection via exec() -----------------------------------
@app.route("/transform", methods=["POST"])
def transform():
    code = request.json.get("code", "")
    data = request.json.get("data", [])
    # VULNERABLE: user-supplied code executed directly
    namespace = {"data": data, "result": None}
    try:
        exec(code, namespace)
        return jsonify(result=namespace.get("result"))
    except Exception as e:
        return jsonify(error=str(e)), 400


# -- CWE-611: XML External Entity Injection ------------------------------
@app.route("/parse-xml", methods=["POST"])
def parse_xml():
    xml_data = request.get_data(as_text=True)
    # VULNERABLE: default parser allows XXE
    tree = ET.fromstring(xml_data)
    return jsonify(tag=tree.tag, text=tree.text)


# -- CWE-117: Log Injection ----------------------------------------------
@app.route("/log-action", methods=["POST"])
def log_action():
    user = request.json.get("user", "anonymous")
    action = request.json.get("action", "unknown")
    # VULNERABLE: unsanitized user input in log message
    logger.info(f"User {user} performed action: {action}")
    return jsonify(status="logged")


# -- Unsafe YAML Loading -------------------------------------------------
def load_config(path: str) -> dict:
    import yaml

    with open(path) as f:
        # VULNERABLE: yaml.load without SafeLoader allows code execution
        return yaml.load(f, Loader=yaml.FullLoader)

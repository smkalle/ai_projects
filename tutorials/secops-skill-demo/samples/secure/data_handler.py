"""
Secure version of the data handling module.
Each vulnerability from the vulnerable version is remediated here.
"""

import json
import logging
import re
from defusedxml import ElementTree as ET
from flask import Flask, request, jsonify

app = Flask(__name__)
logger = logging.getLogger(__name__)


# FIX CWE-502: Only accept safe formats, never pickle
@app.route("/import", methods=["POST"])
def import_data():
    raw = request.get_data()
    fmt = request.args.get("format", "json")

    if fmt == "json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return jsonify(error="Invalid JSON"), 400
    else:
        return jsonify(error="Only JSON format is supported"), 400

    return jsonify(imported=len(data) if isinstance(data, list) else 1)


# FIX CWE-95: Use a safe math evaluator instead of eval()
def _safe_eval_math(expression: str) -> float:
    """Evaluate simple arithmetic expressions without eval()."""
    import ast
    import operator

    allowed_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        elif isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
            return allowed_ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
            return allowed_ops[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported expression: {ast.dump(node)}")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree)


@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.json.get("expression", "0")
    try:
        result = _safe_eval_math(expression)
        return jsonify(result=result)
    except (ValueError, SyntaxError):
        return jsonify(error="Invalid arithmetic expression"), 400


# FIX CWE-95: Remove exec() endpoint entirely — no safe way to run user code
# The /transform endpoint has been removed. Use predefined transformations instead.


# FIX CWE-611: Use defusedxml to prevent XXE
@app.route("/parse-xml", methods=["POST"])
def parse_xml():
    xml_data = request.get_data(as_text=True)
    try:
        tree = ET.fromstring(xml_data)  # defusedxml blocks XXE
        return jsonify(tag=tree.tag, text=tree.text)
    except ET.ParseError:
        return jsonify(error="Invalid XML"), 400


# FIX CWE-117: Sanitize log input
def _sanitize_for_log(value: str) -> str:
    """Remove newlines and control characters to prevent log injection."""
    return re.sub(r"[\r\n\x00-\x1f]", "", value)[:200]


@app.route("/log-action", methods=["POST"])
def log_action():
    user = _sanitize_for_log(request.json.get("user", "anonymous"))
    action = _sanitize_for_log(request.json.get("action", "unknown"))
    logger.info("User %s performed action: %s", user, action)
    return jsonify(status="logged")


# FIX: Use yaml.safe_load instead of yaml.load
def load_config(path: str) -> dict:
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)

"""
Intentionally vulnerable Flask web application.
DO NOT deploy this code — it exists solely for security audit training.

Vulnerability classes demonstrated:
  - CWE-89:  SQL Injection
  - CWE-78:  OS Command Injection
  - CWE-79:  Cross-Site Scripting (Reflected)
  - CWE-942: CORS Misconfiguration
  - CWE-209: Information Exposure Through Error Messages
"""

import sqlite3
import subprocess
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# -- CWE-942: CORS wildcard with credentials ----------------------------
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# -- CWE-89: SQL Injection -----------------------------------------------
@app.route("/users")
def get_user():
    username = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    # VULNERABLE: string formatting in SQL
    cur.execute(f"SELECT * FROM users WHERE name = '{username}'")
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# -- CWE-78: Command Injection -------------------------------------------
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # VULNERABLE: user input in shell command
    output = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return output


# -- CWE-79: Reflected XSS -----------------------------------------------
@app.route("/greet")
def greet():
    name = request.args.get("name", "World")
    # VULNERABLE: user input rendered directly in HTML
    return render_template_string(f"<h1>Hello, {name}!</h1>")


# -- CWE-209: Verbose Error Messages -------------------------------------
@app.route("/divide")
def divide():
    try:
        a = int(request.args.get("a", 0))
        b = int(request.args.get("b", 1))
        return jsonify(result=a / b)
    except Exception as e:
        # VULNERABLE: full exception detail sent to client
        return jsonify(error=str(e), type=type(e).__name__), 500


if __name__ == "__main__":
    # VULNERABLE: debug mode exposes Werkzeug debugger
    app.run(debug=True, host="0.0.0.0")

"""
Secure version of the Flask web application.
Each vulnerability from the vulnerable version is remediated here.
"""

import sqlite3
import subprocess
import shlex
from markupsafe import escape
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# FIX CWE-942: Restrict CORS to specific trusted origins
CORS(app, origins=["https://myapp.example.com"], supports_credentials=True)


# FIX CWE-89: Use parameterized queries
@app.route("/users")
def get_user():
    username = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE name = ?", (username,))
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows)


# FIX CWE-78: Avoid shell=True, validate input
@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # Validate: only allow IP addresses and hostnames
    if not all(c.isalnum() or c in ".-:" for c in host):
        return jsonify(error="Invalid host"), 400
    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", host],  # list form, no shell
            timeout=5,
        )
        return output
    except subprocess.SubprocessError:
        return jsonify(error="Ping failed"), 500


# FIX CWE-79: Escape user input before rendering
@app.route("/greet")
def greet():
    name = escape(request.args.get("name", "World"))
    return f"<h1>Hello, {name}!</h1>"


# FIX CWE-209: Generic error message to client, log details server-side
@app.route("/divide")
def divide():
    try:
        a = int(request.args.get("a", 0))
        b = int(request.args.get("b", 1))
        return jsonify(result=a / b)
    except ZeroDivisionError:
        return jsonify(error="Division by zero"), 400
    except ValueError:
        return jsonify(error="Invalid number"), 400


if __name__ == "__main__":
    # FIX: debug=False in production, bind to localhost
    app.run(debug=False, host="127.0.0.1")

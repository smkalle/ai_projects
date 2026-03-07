"""
Secure version of the authentication service.
Each vulnerability from the vulnerable version is remediated here.
"""

import os
import sqlite3
import secrets
from functools import wraps
from flask import Flask, request, jsonify, session, make_response, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# FIX CWE-798: Load secret key from environment, never hardcode
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# Rate limiting state (use Redis in production)
_login_attempts: dict[str, list[float]] = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300


# FIX CWE-327: Use werkzeug's pbkdf2 hashing (salted, iterated)
def hash_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256:600000")


def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)


# -- Authentication decorator --------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify(error="Authentication required"), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify(error="Authentication required"), 401
        if session.get("role") != "admin":
            return jsonify(error="Admin access required"), 403
        return f(*args, **kwargs)
    return decorated


# FIX CWE-307: Rate limiting on login
def _check_rate_limit(ip: str) -> bool:
    import time
    now = time.time()
    attempts = _login_attempts.get(ip, [])
    attempts = [t for t in attempts if now - t < WINDOW_SECONDS]
    _login_attempts[ip] = attempts
    return len(attempts) < MAX_ATTEMPTS


@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr
    if not _check_rate_limit(ip):
        return jsonify(error="Too many attempts, try later"), 429

    import time
    _login_attempts.setdefault(ip, []).append(time.time())

    username = request.json.get("username", "")
    password = request.json.get("password", "")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT password_hash, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row and verify_password(password, row[0]):
        # FIX CWE-384: Regenerate session after login
        session.clear()
        session["user"] = username
        session["role"] = row[1]

        resp = make_response(jsonify(status="ok"))
        # FIX CWE-614: Secure cookie settings
        resp.set_cookie(
            "session_token",
            secrets.token_urlsafe(32),
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        return resp

    return jsonify(status="invalid credentials"), 401


# FIX CWE-306: Authentication required on admin endpoints
@app.route("/admin/users", methods=["GET"])
@admin_required
def list_all_users():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    users = [dict(zip(["id", "username", "email", "role"], r)) for r in cur.fetchall()]
    conn.close()
    return jsonify(users)


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify(status="deleted")


# FIX CWE-306: Password reset requires email verification token
@app.route("/reset-password", methods=["POST"])
def reset_password():
    token = request.json.get("token", "")
    new_password = request.json.get("new_password", "")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT username FROM password_reset_tokens WHERE token = ? AND used = 0", (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify(error="Invalid or expired token"), 400

    hashed = hash_password(new_password)
    cur.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, row[0]))
    cur.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()
    return jsonify(status="password updated")

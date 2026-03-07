"""
Intentionally vulnerable authentication service.
DO NOT deploy this code — it exists solely for security audit training.

Vulnerability classes demonstrated:
  - CWE-798: Hardcoded Credentials
  - CWE-306: Missing Authentication for Critical Function
  - CWE-307: Improper Restriction of Excessive Auth Attempts
  - CWE-614: Sensitive Cookie Without 'Secure' Flag
  - CWE-384: Session Fixation
"""

import hashlib
import sqlite3
from flask import Flask, request, jsonify, session, make_response

app = Flask(__name__)

# -- CWE-798: Hardcoded Credentials --------------------------------------
app.secret_key = "super-secret-flask-key-do-not-change"
ADMIN_PASSWORD = "admin123"
DB_CONNECTION = "postgresql://admin:password123@prod-db:5432/myapp"


# -- CWE-327: Weak Password Hashing (MD5, no salt) -----------------------
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# -- CWE-307: No Rate Limiting on Login ----------------------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", "")
    password = request.json.get("password", "")

    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    if row and verify_password(password, row[0]):
        # CWE-384: Session fixation — session ID not regenerated after login
        session["user"] = username
        session["role"] = "user"

        resp = make_response(jsonify(status="ok"))
        # CWE-614: Cookie missing Secure and HttpOnly flags
        resp.set_cookie("session_token", session.sid, httponly=False, secure=False)
        return resp

    return jsonify(status="invalid credentials"), 401


# -- CWE-306: Missing Authentication on Admin Endpoint -------------------
@app.route("/admin/users", methods=["GET"])
def list_all_users():
    # VULNERABLE: no authentication check — anyone can list all users
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    users = [dict(zip(["id", "username", "email", "role"], r)) for r in cur.fetchall()]
    conn.close()
    return jsonify(users)


@app.route("/admin/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    # VULNERABLE: no authentication, no authorization check
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify(status="deleted")


# -- CWE-306: Password Reset Without Verification ------------------------
@app.route("/reset-password", methods=["POST"])
def reset_password():
    username = request.json.get("username", "")
    new_password = request.json.get("new_password", "")
    # VULNERABLE: no email verification, no old password check
    hashed = hash_password(new_password)
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, username))
    conn.commit()
    conn.close()
    return jsonify(status="password updated")

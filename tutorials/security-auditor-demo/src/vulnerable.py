import sqlite3
import os
import pickle
import subprocess
from flask import Flask, request

app = Flask(__name__)

# Hardcoded credentials (vulnerability)
API_KEY = "AKIA1234567890ABCDEF"
SECRET_KEY = "supersecretpassword123"
DATABASE_PASSWORD = "admin123"  # Another hardcoded password

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable: SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    res = cursor.fetchone()
    conn.close()
    return bool(res)

@app.route('/search')
def search():
    # Vulnerable: Command injection
    query = request.args.get('q', '')
    result = subprocess.check_output(f"grep -r '{query}' /tmp", shell=True)
    return result

@app.route('/load_data')
def load_data():
    # Vulnerable: Insecure deserialization
    data = request.args.get('data', '')
    obj = pickle.loads(data.encode())
    return str(obj)

@app.route('/download')
def download():
    # Vulnerable: Path traversal
    filename = request.args.get('file', '')
    filepath = os.path.join('/var/www/files', filename)
    with open(filepath, 'r') as f:
        return f.read()

def weak_crypto(data):
    # Vulnerable: Weak crypto (MD5)
    import hashlib
    return hashlib.md5(data.encode()).hexdigest()

# CORS misconfiguration
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response
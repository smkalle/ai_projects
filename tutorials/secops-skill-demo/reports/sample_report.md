# Security Audit Report

**Target:** `samples/vulnerable/`
**Files scanned:** 5
**Date:** 2026-03-07
**Tool:** Claude Code + SecOps Skill v1.0.0
**Findings:** 15 (Critical: 4, High: 5, Medium: 4, Low: 2)

---

## Critical Findings

### Finding 1: SQL Injection in get_user()

- **Severity:** Critical
- **CWE:** CWE-89 Improper Neutralization of Special Elements used in an SQL Command
- **Location:** `web_app.py:36`
- **Description:** User input from query parameter `name` is interpolated directly into a SQL query using an f-string, allowing arbitrary SQL execution.
- **Reproducer:** `GET /users?name=' OR '1'='1' --`
- **Fix:** Use parameterized query: `cur.execute("SELECT * FROM users WHERE name = ?", (username,))`
- **Impact:** Full database read/write access. Authentication bypass. Data exfiltration.

### Finding 2: OS Command Injection in ping()

- **Severity:** Critical
- **CWE:** CWE-78 Improper Neutralization of Special Elements used in an OS Command
- **Location:** `web_app.py:43`
- **Description:** User input passed to `subprocess.check_output()` with `shell=True`, allowing arbitrary command execution.
- **Reproducer:** `GET /ping?host=127.0.0.1;cat%20/etc/passwd`
- **Fix:** Use list form: `subprocess.check_output(["ping", "-c", "1", host])` and validate input.
- **Impact:** Remote Code Execution (RCE). Full server compromise.

### Finding 3: Insecure Deserialization via pickle

- **Severity:** Critical
- **CWE:** CWE-502 Deserialization of Untrusted Data
- **Location:** `data_handler.py:24`
- **Description:** `pickle.loads()` called on user-supplied data, allowing arbitrary Python object instantiation and code execution.
- **Reproducer:** POST `/import?format=pickle` with a crafted pickle payload that executes `os.system("id")`.
- **Fix:** Remove pickle support entirely. Accept only JSON.
- **Impact:** Remote Code Execution (RCE). Full server compromise.

### Finding 4: Code Injection via eval()

- **Severity:** Critical
- **CWE:** CWE-95 Improper Neutralization of Directives in Dynamically Evaluated Code
- **Location:** `data_handler.py:33`
- **Description:** `eval()` called directly on user input from JSON body with no sanitization.
- **Reproducer:** `POST /calculate {"expression": "__import__('os').system('id')"}`
- **Fix:** Replace with AST-based safe math evaluator (see `samples/secure/data_handler.py`).
- **Impact:** Remote Code Execution (RCE). Full server compromise.

---

## High Findings

### Finding 5: Reflected Cross-Site Scripting (XSS)

- **Severity:** High
- **CWE:** CWE-79 Improper Neutralization of Input During Web Page Generation
- **Location:** `web_app.py:50`
- **Description:** User input rendered directly in HTML via `render_template_string()` f-string.
- **Reproducer:** `GET /greet?name=<script>alert(document.cookie)</script>`
- **Fix:** Use `markupsafe.escape()` on user input before rendering.
- **Impact:** Session hijacking. Credential theft. Phishing.

### Finding 6: Path Traversal (read + write)

- **Severity:** High
- **CWE:** CWE-22 Improper Limitation of a Pathname to a Restricted Directory
- **Location:** `file_server.py:19` and `file_server.py:26`
- **Description:** User-controlled filename joined with base path without normalization. `../` sequences escape the upload directory.
- **Reproducer:** `GET /files/../../etc/passwd`
- **Fix:** Use `os.path.realpath()` and verify the resolved path starts with the base directory.
- **Impact:** Arbitrary file read. Arbitrary file write (overwrite system files).

### Finding 7: Server-Side Request Forgery (SSRF)

- **Severity:** High
- **CWE:** CWE-918 Server-Side Request Forgery
- **Location:** `file_server.py:34`
- **Description:** User-supplied URL fetched without any host validation. Attacker can reach internal services, cloud metadata, etc.
- **Reproducer:** `GET /fetch?url=http://169.254.169.254/latest/meta-data/`
- **Fix:** Validate URL against an allowlist of permitted hosts and schemes.
- **Impact:** Access to internal services. Cloud credential theft via metadata API. Internal network scanning.

### Finding 8: Hardcoded Credentials

- **Severity:** High
- **CWE:** CWE-798 Use of Hard-Coded Credentials
- **Location:** `auth_service.py:17-18`
- **Description:** Flask secret key, admin password, and database connection string hardcoded in source code.
- **Fix:** Load all secrets from environment variables using `os.environ[]`.
- **Impact:** Full application compromise if source code is exposed.

### Finding 9: Missing Authentication on Admin Endpoints

- **Severity:** High
- **CWE:** CWE-306 Missing Authentication for Critical Function
- **Location:** `auth_service.py:56` and `auth_service.py:65`
- **Description:** Admin endpoints for listing and deleting users have no authentication or authorization checks.
- **Reproducer:** `GET /admin/users` — returns all users without login. `DELETE /admin/users/1` — deletes user without auth.
- **Fix:** Add `@login_required` and `@admin_required` decorators.
- **Impact:** Unauthorized data access. Account deletion by unauthenticated users.

---

## Medium Findings

### Finding 10: Weak Password Hashing (MD5, no salt)

- **Severity:** Medium
- **CWE:** CWE-328 Use of Weak Hash
- **Location:** `auth_service.py:23` and `crypto_utils.py:49`
- **Description:** Passwords hashed with plain MD5 — no salt, fast to brute-force, collision-prone.
- **Fix:** Use PBKDF2-SHA256 with 600,000 iterations and random salt.
- **Impact:** Offline password cracking in seconds with rainbow tables.

### Finding 11: Predictable Random Token Generation

- **Severity:** Medium
- **CWE:** CWE-330 Use of Insufficiently Random Values
- **Location:** `crypto_utils.py:59`
- **Description:** Auth tokens generated with `random.choice()` (Mersenne Twister PRNG), which is predictable.
- **Fix:** Use `secrets.token_urlsafe()` for cryptographic randomness.
- **Impact:** Token prediction. Account takeover.

### Finding 12: AES-ECB Mode Leaks Patterns

- **Severity:** Medium
- **CWE:** CWE-327 Use of a Broken or Risky Cryptographic Algorithm
- **Location:** `crypto_utils.py:33`
- **Description:** AES in ECB mode encrypts identical blocks to identical ciphertext, leaking data patterns.
- **Fix:** Use AES-GCM (authenticated encryption with random nonce).
- **Impact:** Partial plaintext recovery from ciphertext analysis.

### Finding 13: CORS Wildcard with Credentials

- **Severity:** Medium
- **CWE:** CWE-942 Permissive Cross-domain Policy
- **Location:** `web_app.py:22-25`
- **Description:** `Access-Control-Allow-Origin: *` combined with `Allow-Credentials: true` allows any site to make authenticated requests.
- **Fix:** Restrict origins to specific trusted domains.
- **Impact:** Cross-site request forgery via CORS. Data theft from authenticated sessions.

---

## Low Findings

### Finding 14: Verbose Error Messages

- **Severity:** Low
- **CWE:** CWE-209 Generation of Error Message Containing Sensitive Information
- **Location:** `web_app.py:60`
- **Description:** Exception type and message returned to client, revealing internal implementation details.
- **Fix:** Return generic error messages. Log details server-side.
- **Impact:** Information disclosure aiding further attacks.

### Finding 15: Debug Mode Enabled

- **Severity:** Low
- **CWE:** CWE-489 Active Debug Code
- **Location:** `web_app.py:64`
- **Description:** Flask debug mode enables Werkzeug interactive debugger, which allows arbitrary code execution if accessible.
- **Fix:** Set `debug=False` in production.
- **Impact:** Remote code execution via debugger PIN (if reachable).

---

## Summary

| Category | Vulnerable Files | Findings |
|----------|-----------------|----------|
| Injection (SQLi, CMDi, XSS, eval) | web_app.py, data_handler.py | 4 |
| Authentication & Authorization | auth_service.py | 3 |
| Cryptography | crypto_utils.py, auth_service.py | 3 |
| File Handling (traversal, SSRF, upload) | file_server.py | 2 |
| Configuration (CORS, debug, errors) | web_app.py | 3 |

## Remediation

All findings have been remediated in `samples/secure/`. Each secure file maps 1:1 to its vulnerable counterpart with inline comments explaining the fix.

**Priority order:**
1. Critical injection flaws (RCE risk) — fix in hours
2. Missing authentication — fix in hours
3. Hardcoded secrets — fix in hours
4. Weak cryptography — fix within days
5. Configuration issues — fix within sprint

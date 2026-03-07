"""
Intentionally vulnerable cryptography module.
DO NOT deploy this code — it exists solely for security audit training.

Vulnerability classes demonstrated:
  - CWE-327: Use of a Broken or Risky Cryptographic Algorithm
  - CWE-328: Use of Weak Hash
  - CWE-330: Use of Insufficiently Random Values
  - CWE-321: Use of Hard-Coded Cryptographic Key
  - CWE-326: Inadequate Encryption Strength
"""

import hashlib
import random
import string
import base64
from Crypto.Cipher import AES, DES


# -- CWE-321: Hard-Coded Encryption Key ----------------------------------
ENCRYPTION_KEY = b"my-secret-key-16"  # 16 bytes for AES-128
IV = b"0000000000000000"              # static IV


# -- CWE-327 + CWE-326: DES is broken, 56-bit key -----------------------
def encrypt_legacy(plaintext: bytes) -> bytes:
    """Encrypt using DES — broken algorithm with tiny key size."""
    key = b"8bytekey"  # DES requires 8-byte key
    cipher = DES.new(key, DES.MODE_ECB)  # ECB mode leaks patterns
    # pad to 8-byte boundary
    padded = plaintext + b"\x00" * (8 - len(plaintext) % 8)
    return cipher.encrypt(padded)


# -- CWE-327: AES-ECB leaks patterns ------------------------------------
def encrypt_ecb(plaintext: bytes) -> bytes:
    """Encrypt using AES-ECB — leaks repeated block patterns."""
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_ECB)
    padded = plaintext + b"\x00" * (16 - len(plaintext) % 16)
    return cipher.encrypt(padded)


# -- CWE-327: AES-CBC with static IV ------------------------------------
def encrypt_cbc(plaintext: bytes) -> bytes:
    """Encrypt using AES-CBC — static IV makes it deterministic."""
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, IV)
    padded = plaintext + b"\x00" * (16 - len(plaintext) % 16)
    return cipher.encrypt(padded)


# -- CWE-328: MD5 for password hashing ----------------------------------
def hash_password(password: str) -> str:
    """Hash a password using MD5 — collision-prone, no salt."""
    return hashlib.md5(password.encode()).hexdigest()


# -- CWE-328: SHA1 for integrity ----------------------------------------
def sign_message(message: str, secret: str) -> str:
    """Sign a message using SHA1 — vulnerable to length extension attacks."""
    return hashlib.sha1((secret + message).encode()).hexdigest()


# -- CWE-330: Predictable random for tokens -----------------------------
def generate_token(length: int = 32) -> str:
    """Generate an auth token using math/random — predictable PRNG."""
    # VULNERABLE: random.choice is not cryptographically secure
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_reset_code() -> str:
    """Generate a password reset code — predictable and short."""
    # VULNERABLE: only 4 digits, easily brute-forced
    return str(random.randint(1000, 9999))


# -- CWE-327: Base64 is not encryption ----------------------------------
def encrypt_sensitive(data: str) -> str:
    """'Encrypt' data using base64 — this is encoding, not encryption."""
    # VULNERABLE: base64 is encoding, not encryption — trivially reversible
    return base64.b64encode(data.encode()).decode()


def decrypt_sensitive(encoded: str) -> str:
    return base64.b64decode(encoded.encode()).decode()

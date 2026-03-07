"""
Secure version of the cryptography module.
Each vulnerability from the vulnerable version is remediated here.
"""

import hashlib
import hmac
import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


# FIX CWE-321: Load encryption key from environment
def _get_encryption_key() -> bytes:
    """Load a 256-bit key from environment. Never hardcode."""
    key_hex = os.environ["ENCRYPTION_KEY_HEX"]  # 64-char hex string
    return bytes.fromhex(key_hex)


# FIX CWE-327 + CWE-326: Use AES-256-GCM (authenticated encryption)
def encrypt(plaintext: bytes) -> bytes:
    """Encrypt using AES-256-GCM with random nonce."""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit random nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext  # prepend nonce for decryption


def decrypt(data: bytes) -> bytes:
    """Decrypt AES-256-GCM ciphertext."""
    key = _get_encryption_key()
    aesgcm = AESGCM(key)
    nonce, ciphertext = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)


# FIX CWE-328: Use PBKDF2-SHA256 with salt and high iteration count
def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-SHA256 with random salt."""
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    key = kdf.derive(password.encode())
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    salt_hex, key_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600_000,
    )
    try:
        kdf.verify(password.encode(), bytes.fromhex(key_hex))
        return True
    except Exception:
        return False


# FIX CWE-328: Use HMAC-SHA256 for message signing
def sign_message(message: str, secret: str) -> str:
    """Sign a message using HMAC-SHA256 — resistant to length extension."""
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def verify_signature(message: str, secret: str, signature: str) -> bool:
    """Verify HMAC-SHA256 signature with constant-time comparison."""
    expected = sign_message(message, secret)
    return hmac.compare_digest(expected, signature)


# FIX CWE-330: Use secrets module for cryptographic randomness
def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure auth token."""
    return secrets.token_urlsafe(length)


def generate_reset_code() -> str:
    """Generate a secure password reset code — 8 chars, alphanumeric."""
    return secrets.token_hex(16)  # 32 hex chars, 128 bits of entropy

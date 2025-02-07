#!/usr/bin/env python3

import logging

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

# Setup Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("EncryptionTest")

# Generate a 256-bit (32-byte) AES key for testing
SECRET_KEY = get_random_bytes(32)

def encrypt_data(plaintext: str) -> str:
    """
    Encrypts plaintext using AES-GCM encryption and returns a Base64-encoded string.
    """
    try:
        if len(SECRET_KEY) not in [16, 24, 32]:
            raise ValueError("Invalid SECRET_KEY length. Must be 16, 24, or 32 bytes.")

        cipher = AES.new(SECRET_KEY, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        encrypted_data = cipher.nonce + tag + ciphertext
        encrypted_b64 = b64encode(encrypted_data).decode("utf-8")

        logger.debug(f"[DEBUG] Encrypted Data (Base64): {encrypted_b64}")
        return encrypted_b64

    except Exception as e:
        logger.error(f"[ERROR] Encryption failed: {e}")
        return ""

def decrypt_data(ciphertext_b64: str) -> str:
    """
    Decrypts a Base64-encoded AES-GCM encrypted string and returns the original plaintext.
    """
    try:
        if not ciphertext_b64:
            return "{}"

        raw = b64decode(ciphertext_b64)
        nonce = raw[:16]
        tag = raw[16:32]
        ciphertext = raw[32:]

        cipher = AES.new(SECRET_KEY, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        logger.debug(f"[DEBUG] Decrypted Data: {plaintext.decode('utf-8')}")
        return plaintext.decode("utf-8")

    except Exception as e:
        logger.error(f"[ERROR] Decryption failed: {e}")
        return "{}"

# ===============================
# 🔹 TEST CASES
# ===============================
def test_encryption():
    """
    Tests the encryption and decryption process.
    """
    test_strings = [
        "Hello, World!",  # Simple text
        "FastAPI is awesome!",  # Longer text
        "1234567890!@#$%^&*()",  # Special characters
        "This is a test of AES encryption.",  # Full sentence
        "",  # Empty string test
        "🔒 Secure Data! 🔑",  # Unicode characters
    ]

    for i, test_text in enumerate(test_strings):
        logger.info(f"🔍 Test {i+1}: Encrypting -> {test_text}")

        encrypted = encrypt_data(test_text)
        if not encrypted:
            logger.error(f"❌ Test {i+1} Failed: Encryption returned empty string.")
            continue

        decrypted = decrypt_data(encrypted)
        if decrypted != test_text:
            logger.error(f"❌ Test {i+1} Failed: Decrypted output does not match original text.")
        else:
            logger.info(f"✅ Test {i+1} Passed: Decryption successful.")

if __name__ == "__main__":
    test_encryption()
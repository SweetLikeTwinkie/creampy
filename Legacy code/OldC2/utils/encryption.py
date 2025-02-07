from config import extract_config_values
from Crypto.Cipher import AES
from logging_config import logger
from base64 import b64encode, b64decode


SECRET_KEY = extract_config_values('SECRET_KEY')


def encrypt_data(plaintext: str) -> str:
    """
    Encrypts the given plaintext using AES-GCM encryption and returns a Base64-encoded string.

    AES-GCM (Galois/Counter Mode) ensures both confidentiality and integrity, making it resistant
    to tampering and data forgery.

    :param plaintext: The text data to be encrypted.
    :return: A Base64-encoded string containing the encrypted data, including the nonce, authentication tag,
             and ciphertext. Returns an empty string if encryption fails.
    """
    try:
        # Ensure SECRET_KEY is valid.
        if len(SECRET_KEY) not in [16, 24, 32]:
            raise ValueError("The secret key must be 16, 24, or 32 bytes long.")
        cipher = AES.new(SECRET_KEY, AES.MODE_GCM) # Crea AES-GCM cipher
        # Encrypt and generate an authentication tag
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode("utf-8"))
        encrypted = cipher.nonce + tag + ciphertext     # Combine nonce, tag, and ciphertext
        logger.debug(f"[DEBUG] Encrypted data: {encrypted}")
        return b64encode(encrypted).decode("utf-8") # Convert to Base64 for safe storage/transmission
    except Exception as e:
        logger.error(f"[ERROR] Encryption failed: {e}")
        return ""


def decrypt_data(ciphertext_b64: str) -> str:
    """
    Decrypts a Base64-encoded AES-GCM encrypted string and returns the original plaintext.

    The function expects an encrypted string that was previously generated using `encrypt_data()`.
    It extracts the nonce, authentication tag, and ciphertext, then decrypts and verifies
    the integrity of the message using AES-GCM.

    :param ciphertext_b64: A Base64-encoded encrypted string containing nonce, tag, and ciphertext.
    :return: The decrypted plaintext string. If decryption fails, an empty JSON object (`{}`) is returned.
    """
    try:
        if not ciphertext_b64:
            return "{}" # Return empty JSON object if no ciphertext is provided.
        raw = b64decode(ciphertext_b64) # Decode Base64 string into raw encrypted bytes
        # Extract nonce (first 16 bytes), authentication tag (next 16 bytes), and ciphertext (remaining bytes)
        nonce = raw[:16]
        tag = raw[16:32]
        ciphertext = raw[32:]
        cipher = AES.new(SECRET_KEY, AES.MODE_GCM, nonce=nonce) # Create a new AES cipher with the extracted nonce
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)  # Decrypt and verify the integrity of the message
        logger.debug(f"[DEBUG] Decrypted data: {plaintext}")
        return plaintext.decode("utf-8")  # Convert bytes to string
    except Exception as e:
        logger.error(f"[ERROR] Decryption failed: {e}")
        return "{}" # Return empty JSON object on failure
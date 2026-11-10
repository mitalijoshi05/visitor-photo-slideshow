import hashlib
import hmac
import os


def hash_pin(pin: str) -> str:
    """PIN ko salt ke saath hash karta hai. Format: salt$hash"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    return salt.hex() + "$" + digest.hex()


def verify_pin(pin: str, stored: str) -> bool:
    """Check karta hai ki diya hua PIN stored hash se match karta hai ya nahi."""
    salt_hex, hash_hex = stored.split("$")
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    return hmac.compare_digest(digest.hex(), hash_hex)
import base64
import hashlib
import hmac
import os
import struct

from pybase.exceptions.errors import CryptoError

# ── constants ──────────────────────────────────────────────────
_SALT_BYTES = 32
_NONCE_BYTES = 16
_TAG_BYTES = 32
_PBKDF2_ITER = 600_000
_KEY_BYTES = 32


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive KEY_BYTES from password using PBKDF2-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PBKDF2_ITER, dklen=_KEY_BYTES
    )


def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
    """Generate |length| bytes of key material using HMAC-SHA256 in counter mode.

    Each 32-byte block is HMAC(key, nonce || counter). This gives us a
    CTR-mode-like stream without needing AES hardware or external deps.
    """
    result = bytearray()
    counter = 0
    while len(result) < length:
        block = hmac.digest(key, nonce + struct.pack(">Q", counter), "sha256")
        result.extend(block)
        counter += 1
    return bytes(result[:length])


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt a string with PBKDF2-derived key + HMAC-CTR + authentication tag.

    Returns base64(salt || nonce || ciphertext || tag).

    Security properties:
        - Unique key per encryption (random salt)
        - Unique keystream per encryption (random nonce)
        - Encrypt-then-MAC authentication (HMAC-SHA256)
        - 600k PBKDF2 iterations
    """
    if plaintext is None:
        return None

    data = str(plaintext).encode("utf-8")
    salt = os.urandom(_SALT_BYTES)
    nonce = os.urandom(_NONCE_BYTES)
    key = _derive_key(password, salt)
    stream = _keystream(key, nonce, len(data))
    ciphertext = bytes(a ^ b for a, b in zip(data, stream))

    # Authenticate: tag = HMAC(key, salt || nonce || ciphertext)
    tag = hmac.digest(key, salt + nonce + ciphertext, "sha256")

    payload = salt + nonce + ciphertext + tag
    return base64.urlsafe_b64encode(payload).decode("utf-8")


def decrypt(payload: str, password: str) -> str:
    """Decrypt a string previously encrypted with encrypt().

    Raises CryptoError if the payload is tampered (tag mismatch).
    """
    if payload is None:
        return None

    try:
        raw = base64.urlsafe_b64decode(payload.encode("utf-8"))
    except Exception as exc:
        raise CryptoError("Payload corrompido: base64 inválido") from exc

    if len(raw) < _SALT_BYTES + _NONCE_BYTES + _TAG_BYTES:
        raise CryptoError("Payload corrompido: tamanho inválido")

    salt = raw[:_SALT_BYTES]
    nonce = raw[_SALT_BYTES:_SALT_BYTES + _NONCE_BYTES]
    ciphertext = raw[_SALT_BYTES + _NONCE_BYTES:-_TAG_BYTES]
    tag = raw[-_TAG_BYTES:]

    key = _derive_key(password, salt)

    # Verify tag (constant-time comparison)
    expected = hmac.digest(key, salt + nonce + ciphertext, "sha256")
    if not hmac.compare_digest(tag, expected):
        raise CryptoError(
            "Payload adulterado ou senha incorreta — tag de autenticação inválida"
        )

    stream = _keystream(key, nonce, len(ciphertext))
    plain_bytes = bytes(a ^ b for a, b in zip(ciphertext, stream))
    return plain_bytes.decode("utf-8")

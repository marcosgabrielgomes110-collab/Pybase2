class PybaseError(Exception):
    """Base exception for all Pybase errors."""


class SchemaError(PybaseError):
    """Raised when a schema definition is invalid."""


class FieldError(PybaseError):
    """Raised when a field operation fails (type mismatch, missing field, etc.)."""


class DatabaseError(PybaseError):
    """Raised when a database operation fails."""


class CryptoError(PybaseError):
    """Raised when encryption or decryption fails."""


class AuthError(PybaseError):
    """Raised when the database password is incorrect."""


__all__ = [
    "PybaseError",
    "SchemaError",
    "FieldError",
    "DatabaseError",
    "CryptoError",
    "AuthError",
]

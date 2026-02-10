"""Token encryption utilities."""
import os
import warnings
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

_FERNET: Optional[Fernet] = None
_PREFIX = "enc:"


def _get_env() -> str:
    return os.getenv("ENVIRONMENT", "DEV").upper()


def _get_fernet() -> Optional[Fernet]:
    global _FERNET
    if _FERNET is not None:
        return _FERNET

    key = os.getenv("TOKEN_ENCRYPTION_KEY")
    if not key:
        if _get_env() == "PROD":
            raise RuntimeError("TOKEN_ENCRYPTION_KEY must be set in production.")
        warnings.warn(
            "TOKEN_ENCRYPTION_KEY not set; tokens will be stored in plaintext in non-prod.",
            RuntimeWarning
        )
        return None

    _FERNET = Fernet(key)
    return _FERNET


def encrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if value.startswith(_PREFIX):
        return value
    fernet = _get_fernet()
    if not fernet:
        return value
    token = fernet.encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{_PREFIX}{token}"


def decrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not value.startswith(_PREFIX):
        return value
    fernet = _get_fernet()
    if not fernet:
        return value
    token = value[len(_PREFIX):]
    try:
        return fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Failed to decrypt token. Check TOKEN_ENCRYPTION_KEY.") from exc

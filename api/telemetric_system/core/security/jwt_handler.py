"""JWT token creation, validation, and refresh.

This module provides thin wrappers that delegate to the primary helpers in
`telemetric_system.core.security.auth` to avoid circular imports in some
contexts while keeping a stable import path.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from telemetric_system.app.config import SETTINGS
from telemetric_system.core.security import auth as _auth


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    return _auth.create_access_token(subject, extra)


def create_refresh_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    return _auth.create_refresh_token(subject, extra)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    return _auth.decode_token(token)


def refresh_tokens(refresh_token: str):
    return _auth.refresh_tokens(refresh_token)


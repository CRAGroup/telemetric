"""Authentication middleware: JWT/session verification and user context.

Provides helpers to extract JWT bearer tokens or API keys from requests,
validate them, and enforce role-based permissions on route handlers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from telemetric_system.core.security.auth import decode_token, has_role, verify_device_api_key


@dataclass
class RequestContext:
    user_id: Optional[int]
    role: Optional[str]
    device_id: Optional[str]


def extract_bearer_token(headers: Dict[str, str]) -> Optional[str]:
    auth = headers.get("Authorization") or headers.get("authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def authenticate_request(headers: Dict[str, str]) -> RequestContext:
    # JWT path
    token = extract_bearer_token(headers)
    if token:
        payload = decode_token(token) or {}
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id:
            return RequestContext(user_id=int(user_id), role=str(role), device_id=None)
    # API key path
    api_key = headers.get("X-API-Key") or headers.get("x-api-key")
    device_id = headers.get("X-Device-ID") or headers.get("x-device-id")
    if api_key and device_id and verify_device_api_key(device_id, api_key):
        return RequestContext(user_id=None, role="device", device_id=device_id)
    return RequestContext(user_id=None, role=None, device_id=None)


def require_roles(headers: Dict[str, str], *roles: str) -> RequestContext:
    ctx = authenticate_request(headers)
    if ctx.user_id is None or (roles and ctx.role not in {str(r) for r in roles}):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
    return ctx

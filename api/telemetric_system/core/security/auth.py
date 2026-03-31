"""Authentication logic and user verification.

Provides:
- User registration and login with bcrypt password hashing
- JWT access/refresh token creation and validation
- Role-based access control helpers
- API key verification for device authentication
- Simple in-memory session management
- Password reset token generation/verification
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional

import bcrypt
import jwt

from telemetric_system.app.config import SETTINGS
from telemetric_system.core.database.connection import get_session
from telemetric_system.models.user import User, UserRole


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ----------------------
# Password hashing
# ----------------------

def hash_password(plain_password: str) -> str:
    if not plain_password:
        raise ValueError("Password required")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ----------------------
# JWT helpers
# ----------------------

def _jwt_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    now = _jwt_now()
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=SETTINGS.jwt.access_token_minutes)).timestamp()),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SETTINGS.jwt.secret, algorithm=SETTINGS.jwt.algorithm)


def create_refresh_token(subject: str, extra: Optional[Dict[str, Any]] = None) -> str:
    now = _jwt_now()
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=SETTINGS.jwt.refresh_token_minutes)).timestamp()),
        "type": "refresh",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, SETTINGS.jwt.secret, algorithm=SETTINGS.jwt.algorithm)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SETTINGS.jwt.secret, algorithms=[SETTINGS.jwt.algorithm])
    except Exception:
        return None


def refresh_tokens(refresh_token: str) -> Optional[TokenPair]:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    access = create_access_token(str(user_id), {"role": payload.get("role")})
    new_refresh = create_refresh_token(str(user_id), {"role": payload.get("role")})
    return TokenPair(access_token=access, refresh_token=new_refresh)


# ----------------------
# Registration / login
# ----------------------

def get_user_by_email(email: str) -> Optional[User]:
    session = get_session()
    try:
        return session.query(User).filter(User.email == email, User.is_deleted.is_(False)).one_or_none()
    finally:
        session.close()


def register_user(email: str, password: str, full_name: Optional[str] = None, role: Optional[str] = None) -> Optional[User]:
    session = get_session()
    try:
        if get_user_by_email(email):
            return None
        user = User(email=email, hashed_password=hash_password(password), full_name=full_name, is_active=True, role=(role or UserRole.VIEWER.value))
        session.add(user)
        session.commit()
        return user
    finally:
        session.close()


def authenticate_user(email: str, password: str) -> Optional[TokenPair]:
    session = get_session()
    try:
        user = session.query(User).filter(User.email == email, User.is_deleted.is_(False), User.is_active.is_(True)).one_or_none()
        if not user or not verify_password(password, user.hashed_password):
            return None
        access = create_access_token(str(user.id), {"role": user.role})
        refresh = create_refresh_token(str(user.id), {"role": user.role})
        return TokenPair(access_token=access, refresh_token=refresh)
    finally:
        session.close()


# ----------------------
# RBAC helpers
# ----------------------

def has_role(payload: Dict[str, Any], *roles: str) -> bool:
    return str(payload.get("role")) in {str(r) for r in roles}


def require_roles(*roles: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token_payload: Optional[Dict[str, Any]] = kwargs.pop("token_payload", None)
            if token_payload is None or (roles and not has_role(token_payload, *roles)):
                raise PermissionError("forbidden")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ----------------------
# API key authentication (devices)
# ----------------------
# For demo purposes, keep a simple in-memory API key store. In production, use DB.
_DEVICE_API_KEYS: Dict[str, str] = {}  # device_id -> api_key


def set_device_api_key(device_id: str, api_key: Optional[str] = None) -> str:
    key = api_key or secrets.token_urlsafe(24)
    _DEVICE_API_KEYS[device_id] = key
    return key


def verify_device_api_key(device_id: str, candidate_key: str) -> bool:
    return _DEVICE_API_KEYS.get(device_id) == candidate_key


# ----------------------
# Session management (in-memory)
# ----------------------
_SESSIONS: Dict[str, Dict[str, Any]] = {}


def create_session(user_id: str) -> str:
    session_id = secrets.token_urlsafe(24)
    _SESSIONS[session_id] = {"user_id": user_id, "created_at": int(time.time())}
    return session_id


def get_session_data(session_id: str) -> Optional[Dict[str, Any]]:
    return _SESSIONS.get(session_id)


def destroy_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)


# ----------------------
# Password reset flow
# ----------------------
_PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}


def create_password_reset_token(user_id: str, ttl_minutes: int = 30) -> str:
    token = secrets.token_urlsafe(24)
    _PASSWORD_RESET_TOKENS[token] = {"user_id": user_id, "exp": int(time.time() + ttl_minutes * 60)}
    return token


def verify_password_reset_token(token: str) -> Optional[str]:
    data = _PASSWORD_RESET_TOKENS.get(token)
    if not data:
        return None
    if data["exp"] < int(time.time()):
        _PASSWORD_RESET_TOKENS.pop(token, None)
        return None
    return str(data["user_id"]) 


def consume_password_reset_token(token: str, new_password: str) -> bool:
    user_id = verify_password_reset_token(token)
    if not user_id:
        return False
    session = get_session()
    try:
        user = session.query(User).filter(User.id == int(user_id)).one_or_none()
        if not user:
            return False
        user.hashed_password = hash_password(new_password)
        session.add(user)
        session.commit()
        _PASSWORD_RESET_TOKENS.pop(token, None)
        return True
    finally:
        session.close()

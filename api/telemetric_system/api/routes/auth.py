"""Authentication routes: register, login, refresh, me."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field

from telemetric_system.core.security import auth as auth_svc


router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
  email: EmailStr
  password: str = Field(..., min_length=6, max_length=128)
  full_name: Optional[str] = None
  role: Optional[str] = None


class LoginRequest(BaseModel):
  email: EmailStr
  password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
  user = auth_svc.register_user(payload.email, payload.password, payload.full_name, payload.role)
  if not user:
    raise HTTPException(status_code=409, detail="user already exists")
  return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


@router.post("/login")
def login(payload: LoginRequest):
  tokens = auth_svc.authenticate_user(payload.email, payload.password)
  if not tokens:
    raise HTTPException(status_code=401, detail="invalid credentials")
  return {"access_token": tokens.access_token, "refresh_token": tokens.refresh_token, "token_type": tokens.token_type}


class RefreshRequest(BaseModel):
  refresh_token: str


@router.post("/refresh")
def refresh(payload: RefreshRequest):
  pair = auth_svc.refresh_tokens(payload.refresh_token)
  if not pair:
    raise HTTPException(status_code=401, detail="invalid refresh token")
  return {"access_token": pair.access_token, "refresh_token": pair.refresh_token, "token_type": pair.token_type}


@router.get("/me")
def me(request: Request):
  from telemetric_system.api.middleware.auth import authenticate_request
  from telemetric_system.models.user import User
  from telemetric_system.core.database.connection import get_session
  
  ctx = authenticate_request(dict(request.headers))
  if not ctx.user_id:
    raise HTTPException(status_code=401, detail="unauthorized")
  
  # Fetch full user details
  session = get_session()
  try:
    user = session.query(User).filter(User.id == ctx.user_id, User.is_deleted.is_(False)).one_or_none()
    if not user:
      raise HTTPException(status_code=404, detail="user not found")
    
    return {
      "user_id": ctx.user_id,
      "role": ctx.role,
      "email": user.email,
      "full_name": user.full_name,
      "is_active": user.is_active
    }
  finally:
    session.close()


class UpdateProfileRequest(BaseModel):
  full_name: Optional[str] = Field(None, max_length=128)
  phone: Optional[str] = Field(None, max_length=32)
  job_title: Optional[str] = Field(None, max_length=128)
  department: Optional[str] = Field(None, max_length=128)


@router.put("/me")
def update_me(request: Request, payload: UpdateProfileRequest):
  from telemetric_system.api.middleware.auth import authenticate_request
  from telemetric_system.models.user import User
  from telemetric_system.core.database.connection import get_session

  ctx = authenticate_request(dict(request.headers))
  if not ctx.user_id:
    raise HTTPException(status_code=401, detail="unauthorized")

  session = get_session()
  try:
    user = session.query(User).filter(User.id == ctx.user_id, User.is_deleted.is_(False)).one_or_none()
    if not user:
      raise HTTPException(status_code=404, detail="user not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
      if hasattr(user, field):
        setattr(user, field, value)

    session.add(user)
    session.commit()
    return {
      "user_id": ctx.user_id,
      "role": ctx.role,
      "email": user.email,
      "full_name": user.full_name,
      "is_active": user.is_active,
    }
  finally:
    session.close()


class ChangePasswordRequest(BaseModel):
  current_password: str = Field(..., min_length=6)
  new_password: str = Field(..., min_length=6)


@router.post("/change-password")
def change_password(request: Request, payload: ChangePasswordRequest):
  from telemetric_system.api.middleware.auth import authenticate_request
  from telemetric_system.models.user import User
  from telemetric_system.core.database.connection import get_session

  ctx = authenticate_request(dict(request.headers))
  if not ctx.user_id:
    raise HTTPException(status_code=401, detail="unauthorized")

  session = get_session()
  try:
    user = session.query(User).filter(User.id == ctx.user_id, User.is_deleted.is_(False)).one_or_none()
    if not user:
      raise HTTPException(status_code=404, detail="user not found")

    if not auth_svc.verify_password(payload.current_password, user.hashed_password):
      raise HTTPException(status_code=400, detail="current password is incorrect")

    user.hashed_password = auth_svc.hash_password(payload.new_password)
    session.add(user)
    session.commit()
    return {"status": "password updated"}
  finally:
    session.close()



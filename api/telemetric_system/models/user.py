"""User/Admin model with RBAC roles.

Represents a system user with role-based access control.
"""

from __future__ import annotations

from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, validates

from .base import BaseModel


class UserRole(PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    DRIVER = "driver"
    VIEWER = "viewer"


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(120))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.VIEWER.value)

    @validates("email")
    def validate_email(self, key: str, value: str) -> str:  # noqa: ARG002
        if not value or "@" not in value:
            raise ValueError("email must be a valid address")
        return value.strip().lower()

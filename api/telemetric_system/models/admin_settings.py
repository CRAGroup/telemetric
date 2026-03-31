"""Admin Settings model definition.

Stores system-wide configuration and settings.
Compatible with Supabase frontend schema.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class AdminSettings(BaseModel):
    __tablename__ = "admin_settings"

    key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    category: Mapped[Optional[str]] = mapped_column(String(64), index=True)

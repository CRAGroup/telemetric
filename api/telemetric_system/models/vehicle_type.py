"""Vehicle Type model definition.

Represents vehicle categories/types for classification.
Compatible with Supabase frontend schema.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class VehicleType(BaseModel):
    __tablename__ = "vehicle_types"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="vehicle_type")
    
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:  # noqa: ARG002
        if not value or len(value) < 2:
            raise ValueError("name must be at least 2 characters")
        return value.strip()

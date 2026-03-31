"""Geofence model definition.

Represents a geofence area and its associations to vehicles.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, Float, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import Base, BaseModel


# Association table between vehicles and geofences
vehicle_geofences = Table(
    "vehicle_geofences",
    Base.metadata,
    Column("vehicle_id", ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True),
    Column("geofence_id", ForeignKey("geofences.id", ondelete="CASCADE"), primary_key=True),
)


class Geofence(BaseModel):
    __tablename__ = "geofences"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(512))

    # Simple circular fence for MVP (center + radius). Polygon variants can be added later.
    center_lat: Mapped[float] = mapped_column(Float, nullable=False)
    center_lng: Mapped[float] = mapped_column(Float, nullable=False)
    radius_m: Mapped[float] = mapped_column(Float, nullable=False)

    vehicles = relationship("Vehicle", secondary=vehicle_geofences, back_populates="geofences")

    @validates("center_lat", "center_lng")
    def validate_geo(self, key: str, value: float) -> float:  # noqa: ARG002
        if key == "center_lat" and not (-90.0 <= value <= 90.0):
            raise ValueError("center_lat must be between -90 and 90")
        if key == "center_lng" and not (-180.0 <= value <= 180.0):
            raise ValueError("center_lng must be between -180 and 180")
        return value

    @validates("radius_m")
    def validate_radius(self, key: str, value: float) -> float:  # noqa: ARG002
        if value <= 0:
            raise ValueError("radius_m must be positive")
        return value

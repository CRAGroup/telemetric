"""Telemetry record model (time-series).

Stores granular telemetry readings per vehicle and (optionally) driver.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class Telemetry(BaseModel):
    __tablename__ = "telemetry_data"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id", ondelete="SET NULL"), index=True)

    timestamp_utc: Mapped[datetime] = mapped_column(index=True, nullable=False)

    # Engine performance
    rpm: Mapped[Optional[int]] = mapped_column(Integer)
    engine_temp_c: Mapped[Optional[float]] = mapped_column(Float)
    oil_pressure_kpa: Mapped[Optional[float]] = mapped_column(Float)
    battery_voltage_v: Mapped[Optional[float]] = mapped_column(Float)
    throttle_pos_pct: Mapped[Optional[float]] = mapped_column(Float)
    engine_load_pct: Mapped[Optional[float]] = mapped_column(Float)

    # Location & speed
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    speed_kph: Mapped[Optional[float]] = mapped_column(Float)
    heading_deg: Mapped[Optional[float]] = mapped_column(Float)
    altitude_m: Mapped[Optional[float]] = mapped_column(Float)

    # Fuel
    fuel_level_pct: Mapped[Optional[float]] = mapped_column(Float)
    fuel_rate_lph: Mapped[Optional[float]] = mapped_column(Float)

    # Behavior flags
    harsh_accel: Mapped[Optional[bool]] = mapped_column(Boolean)
    hard_brake: Mapped[Optional[bool]] = mapped_column(Boolean)
    sharp_corner: Mapped[Optional[bool]] = mapped_column(Boolean)
    speeding: Mapped[Optional[bool]] = mapped_column(Boolean)
    seatbelt_used: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="telemetries")
    driver = relationship("Driver")

    @validates("latitude", "longitude")
    def validate_geo(self, key: str, value: Optional[float]) -> Optional[float]:  # noqa: ARG002
        if value is None:
            return None
        if key == "latitude" and not (-90.0 <= value <= 90.0):
            raise ValueError("latitude must be between -90 and 90")
        if key == "longitude" and not (-180.0 <= value <= 180.0):
            raise ValueError("longitude must be between -180 and 180")
        return value

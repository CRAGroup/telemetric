"""Trip model definition.

Represents a journey for a vehicle (and optionally a driver) with distance and duration.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Trip(BaseModel):
    __tablename__ = "trips"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id", ondelete="SET NULL"), index=True)

    start_time_utc: Mapped[datetime] = mapped_column(nullable=False, index=True)
    end_time_utc: Mapped[Optional[datetime]] = mapped_column(index=True)

    start_lat: Mapped[Optional[float]] = mapped_column(Float)
    start_lng: Mapped[Optional[float]] = mapped_column(Float)
    end_lat: Mapped[Optional[float]] = mapped_column(Float)
    end_lng: Mapped[Optional[float]] = mapped_column(Float)

    distance_km: Mapped[Optional[float]] = mapped_column(Float)
    fuel_used_l: Mapped[Optional[float]] = mapped_column(Float)

    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")

    __table_args__ = (
        CheckConstraint("distance_km IS NULL OR distance_km >= 0", name="ck_trip_distance_nonneg"),
        CheckConstraint("fuel_used_l IS NULL OR fuel_used_l >= 0", name="ck_trip_fuel_nonneg"),
    )

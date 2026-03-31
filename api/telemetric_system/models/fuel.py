"""Fuel transaction model.

Represents refueling events or fuel-related transactions for a vehicle.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class FuelTransaction(BaseModel):
    __tablename__ = "fuel_transactions"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)

    event_time_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    liters: Mapped[float] = mapped_column(Float, nullable=False)
    price_per_liter: Mapped[Optional[float]] = mapped_column(Float)
    station_name: Mapped[Optional[str]] = mapped_column(String(128))
    note: Mapped[Optional[str]] = mapped_column(String(500))

    vehicle = relationship("Vehicle", back_populates="fuel_transactions")

    __table_args__ = (
        CheckConstraint("liters >= 0", name="ck_fuel_liters_nonneg"),
        CheckConstraint("price_per_liter IS NULL OR price_per_liter >= 0", name="ck_fuel_price_nonneg"),
    )

    @validates("liters")
    def validate_liters(self, key: str, value: float) -> float:  # noqa: ARG002
        if value < 0:
            raise ValueError("liters cannot be negative")
        return value

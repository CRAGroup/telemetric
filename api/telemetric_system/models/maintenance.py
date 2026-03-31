"""Maintenance records model.

Represents maintenance or service events for a vehicle.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, Date, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class MaintenanceRecord(BaseModel):
    __tablename__ = "maintenance_records"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)

    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    odometer_km: Mapped[Optional[float]] = mapped_column(Float)
    service_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    cost: Mapped[Optional[float]] = mapped_column(Float)
    mechanic: Mapped[Optional[str]] = mapped_column(String(128))
    priority: Mapped[Optional[str]] = mapped_column(String(20), default="medium")
    record_type: Mapped[Optional[str]] = mapped_column(String(20), default="scheduled")
    status: Mapped[Optional[str]] = mapped_column(String(20), default="pending")
    completed_date: Mapped[Optional[date]] = mapped_column(Date)

    vehicle = relationship("Vehicle", back_populates="maintenance_records")

    __table_args__ = (
        CheckConstraint("odometer_km IS NULL OR odometer_km >= 0", name="ck_maint_odometer_nonneg"),
        CheckConstraint("cost IS NULL OR cost >= 0", name="ck_maint_cost_nonneg"),
    )

    @validates("service_type")
    def validate_service_type(self, key: str, value: str) -> str:  # noqa: ARG002
        if not value:
            raise ValueError("service_type must be provided")
        return value.strip()

"""Alert model definition.

Represents an alert generated from telemetry or rules, linked to a vehicle and
optionally a driver.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class AlertSeverity(PyEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Alert(BaseModel):
    __tablename__ = "alerts"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id", ondelete="SET NULL"), index=True)

    alert_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    message: Mapped[Optional[str]] = mapped_column(String(500))
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default=AlertSeverity.WARNING.value)

    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rule_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    vehicle = relationship("Vehicle", back_populates="alerts")
    driver = relationship("Driver", back_populates="alerts")

    @validates("severity")
    def validate_severity(self, key: str, value: str) -> str:  # noqa: ARG002
        allowed = {s.value for s in AlertSeverity}
        if value not in allowed:
            raise ValueError(f"severity must be one of {sorted(allowed)}")
        return value

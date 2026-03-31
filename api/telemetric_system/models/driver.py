"""Driver model definition.

Represents a driver with personal details and association to assigned vehicles and trips.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import CheckConstraint, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class Driver(BaseModel):
    __tablename__ = "drivers"

    # Core identifiers
    driver_identifier: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Contact information
    phone_number: Mapped[Optional[str]] = mapped_column(String(32))
    email: Mapped[Optional[str]] = mapped_column(String(120), unique=True)
    
    # License information
    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    license_expiry: Mapped[Optional[date]] = mapped_column(Date)
    license_class: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Personal information
    national_id: Mapped[Optional[str]] = mapped_column(String(64))
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    blood_group: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Address
    address: Mapped[Optional[str]] = mapped_column(Text)
    
    # Medical and PSV
    medical_certificate_expiry: Mapped[Optional[date]] = mapped_column(Date)
    psv_badge_number: Mapped[Optional[str]] = mapped_column(String(64))
    psv_badge_expiry: Mapped[Optional[date]] = mapped_column(Date)
    
    # Emergency contacts
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(128))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(32))
    
    # Next of kin
    next_of_kin_name: Mapped[Optional[str]] = mapped_column(String(128))
    next_of_kin_phone: Mapped[Optional[str]] = mapped_column(String(32))
    next_of_kin_relationship: Mapped[Optional[str]] = mapped_column(String(64))
    
    # Experience
    years_experience: Mapped[Optional[int]] = mapped_column(Integer)
    previous_employer: Mapped[Optional[str]] = mapped_column(String(256))
    
    # Status
    status: Mapped[Optional[str]] = mapped_column(String(20), default="active")
    
    # Media
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="driver")
    trips = relationship("Trip", back_populates="driver")
    alerts = relationship("Alert", back_populates="driver")

    __table_args__ = (
        CheckConstraint("length(first_name) >= 1", name="ck_driver_first_name_len"),
        CheckConstraint("length(last_name) >= 1", name="ck_driver_last_name_len"),
    )

    @validates("license_number")
    def validate_license_number(self, key: str, value: str) -> str:  # noqa: ARG002
        if not value or len(value) < 5:
            raise ValueError("license_number must be at least 5 characters")
        return value.strip()

"""Vehicle model definition.

Defines the `Vehicle` ORM model including identifiers, specifications,
assignment to a driver, and operational state.
Compatible with Supabase frontend schema.
"""

from __future__ import annotations

from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseModel


class VehicleStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    IN_TRANSIT = "in_transit"
    AWAITING_LOADING = "awaiting_loading"
    SHIPPED = "shipped"
    IDLE = "idle"


class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    # Core identifiers
    vehicle_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    registration_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    
    # Vehicle specifications
    make: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[Optional[str]] = mapped_column(String(128))  # Supabase compatibility
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin_number: Mapped[Optional[str]] = mapped_column(String(64), unique=True)
    
    # Operational data
    current_odometer: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fuel_tank_capacity: Mapped[Optional[float]] = mapped_column(Float)
    
    # Load tracking (Supabase compatibility)
    max_load_weight: Mapped[Optional[float]] = mapped_column(Float)
    current_load_weight: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    load_category: Mapped[Optional[str]] = mapped_column(String(64))
    
    # Location (Supabase compatibility - from latest telemetry)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    
    # Media
    image_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id", ondelete="SET NULL"), index=True)
    vehicle_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicle_types.id", ondelete="SET NULL"), index=True)
    
    # Status
    status: Mapped[VehicleStatus] = mapped_column(
        SAEnum(VehicleStatus, name="vehicle_status"), nullable=False, default=VehicleStatus.ACTIVE
    )
    
    # Device tracking
    device_imei: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)


    # Relationships
    driver = relationship("Driver", back_populates="vehicles")
    vehicle_type = relationship("VehicleType", back_populates="vehicles")
    telemetries = relationship("Telemetry", back_populates="vehicle", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_records = relationship(
        "MaintenanceRecord", back_populates="vehicle", cascade="all, delete-orphan"
    )
    fuel_transactions = relationship("FuelTransaction", back_populates="vehicle", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="vehicle", cascade="all, delete-orphan")
    geofences = relationship("Geofence", secondary="vehicle_geofences", back_populates="vehicles")

    __table_args__ = (
        CheckConstraint("year >= 1900 AND year <= 2100", name="ck_vehicle_year_range"),
        CheckConstraint("current_odometer >= 0", name="ck_vehicle_odometer_nonneg"),
        CheckConstraint("current_load_weight IS NULL OR current_load_weight >= 0", name="ck_vehicle_load_nonneg"),
        CheckConstraint("max_load_weight IS NULL OR max_load_weight > 0", name="ck_vehicle_max_load_pos"),
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="ck_vehicle_lat_range"),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="ck_vehicle_lng_range"),
    )

    # Validations
    @validates("registration_number")
    def validate_registration(self, key: str, value: str) -> str:  # noqa: ARG002
        if not value or len(value) < 3:
            raise ValueError("registration_number must be at least 3 characters")
        return value.strip()

    @validates("year")
    def validate_year(self, key: str, value: int) -> int:  # noqa: ARG002
        if value < 1900 or value > 2100:
            raise ValueError("year must be between 1900 and 2100")
        return value

    @validates("current_odometer")
    def validate_odometer(self, key: str, value: float) -> float:  # noqa: ARG002
        if value < 0:
            raise ValueError("current_odometer cannot be negative")
        return value
    
    @validates("latitude", "longitude")
    def validate_coordinates(self, key: str, value: Optional[float]) -> Optional[float]:  # noqa: ARG002
        if value is None:
            return None
        if key == "latitude" and not (-90.0 <= value <= 90.0):
            raise ValueError("latitude must be between -90 and 90")
        if key == "longitude" and not (-180.0 <= value <= 180.0):
            raise ValueError("longitude must be between -180 and 180")
        return value

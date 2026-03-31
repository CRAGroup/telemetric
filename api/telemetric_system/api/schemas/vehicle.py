"""Vehicle request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VehicleBase(BaseModel):
    registration_number: str = Field(..., min_length=3, max_length=32)
    make: str
    model: str
    year: int = Field(..., ge=1900, le=2100)
    vin_number: Optional[str] = Field(None, max_length=64)
    fuel_tank_capacity: Optional[float] = Field(None, ge=0)
    vehicle_type: Optional[str] = None
    color: Optional[str] = None


class VehicleCreate(VehicleBase):
    vehicle_id: str = Field(..., min_length=3, max_length=50)
    current_odometer: float = Field(0, ge=0)
    driver_id: Optional[int] = None
    status: Optional[str] = Field("active")
    device_imei: Optional[str] = Field(None, max_length=32)


class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


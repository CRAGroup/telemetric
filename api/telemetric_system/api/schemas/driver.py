"""Driver request/response schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class DriverBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    license_number: str = Field(..., min_length=5, max_length=64)
    license_expiry: Optional[date] = None
    phone_number: Optional[str] = Field(None, max_length=32)
    email: Optional[EmailStr] = None


class DriverCreate(DriverBase):
    driver_identifier: str = Field(..., min_length=3, max_length=50)


class DriverResponse(DriverBase):
    id: int
    driver_identifier: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


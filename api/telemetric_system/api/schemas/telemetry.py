"""Telemetry data schemas for ingestion and queries."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TelemetryIngest(BaseModel):
    vehicle_id: Optional[int] = Field(None, description="DB vehicle id")
    vehicle_identifier: Optional[str] = Field(None, description="External vehicle identifier")
    timestamp: Optional[float] = Field(None, description="Unix epoch seconds")
    vehicle: Dict[str, Any] = Field(default_factory=dict)
    engine: Dict[str, Any] = Field(default_factory=dict)


class TelemetryRecord(BaseModel):
    id: int
    vehicle_id: int
    driver_id: Optional[int]
    timestamp_utc: datetime
    rpm: Optional[int]
    engine_temp_c: Optional[float]
    oil_pressure_kpa: Optional[float]
    battery_voltage_v: Optional[float]
    throttle_pos_pct: Optional[float]
    engine_load_pct: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    speed_kph: Optional[float]
    heading_deg: Optional[float]
    altitude_m: Optional[float]
    fuel_level_pct: Optional[float]
    fuel_rate_lph: Optional[float]
    harsh_accel: Optional[bool]
    hard_brake: Optional[bool]
    sharp_corner: Optional[bool]
    speeding: Optional[bool]
    seatbelt_used: Optional[bool]

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    total: int
    items: List[TelemetryRecord]


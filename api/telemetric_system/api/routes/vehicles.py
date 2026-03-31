"""Vehicle CRUD and related endpoints.

FastAPI router providing:
- List/create/get/update/delete vehicles (soft delete)
- Latest telemetry, current location
- Trip history and alerts
Includes pagination/filtering, request validation, and basic docs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import joinedload

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.vehicle import Vehicle, VehicleStatus
from telemetric_system.models.driver import Driver
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.trip import Trip
from telemetric_system.models.alert import Alert
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


# --------------------
# Schemas
# --------------------
class VehicleCreate(BaseModel):
  # Core identifiers - vehicle_id auto-generated from registration_number
  registration_number: str = Field(..., min_length=3, max_length=32)
  
  # Vehicle specifications
  make: str = Field(..., min_length=1, max_length=64)
  model_name: str = Field(..., min_length=1, max_length=128)  # Frontend uses model_name
  body_type: Optional[str] = Field(None, max_length=64)
  chassis_number: Optional[str] = Field(None, max_length=64)
  engine_number: Optional[str] = Field(None, max_length=64)
  engine_capacity: Optional[int] = Field(None, ge=0)
  
  # Load tracking
  max_load_weight: Optional[float] = Field(None, ge=0)
  
  # Operational data
  acquisition_odometer: Optional[float] = Field(0, ge=0)
  
  # Assignment and usage
  department: Optional[str] = Field(None, max_length=128)
  driver_id: Optional[int] = Field(None, description="ID of assigned driver")
  usage_type: Optional[str] = Field(None, max_length=64)
  
  # Documentation
  logbook_details: Optional[str] = None
  spare_keys_location: Optional[str] = None
  
  # Status
  vehicle_status: Optional[str] = Field("idle")
  
  # Insurance
  insurance_provider: Optional[str] = Field(None, max_length=128)
  insurance_policy_number: Optional[str] = Field(None, max_length=64)
  insurance_expiry: Optional[str] = None
  
  # Permits and compliance
  permit_details: Optional[str] = None
  
  # Fuel
  fuel_type: Optional[str] = Field(None, max_length=32)
  
  # Tracking
  tracking_device_id: Optional[str] = Field(None, max_length=32)


class VehicleUpdate(BaseModel):
  # Core identifiers
  registration_number: Optional[str] = Field(None, min_length=3, max_length=32)
  
  # Vehicle specifications
  make: Optional[str] = Field(None, min_length=1, max_length=64)
  model_name: Optional[str] = Field(None, min_length=1, max_length=128)
  body_type: Optional[str] = Field(None, max_length=64)
  chassis_number: Optional[str] = Field(None, max_length=64)
  engine_number: Optional[str] = Field(None, max_length=64)
  engine_capacity: Optional[int] = Field(None, ge=0)
  
  # Load tracking
  max_load_weight: Optional[float] = Field(None, ge=0)
  
  # Operational data
  acquisition_odometer: Optional[float] = Field(None, ge=0)
  current_odometer: Optional[float] = Field(None, ge=0)
  
  # Assignment and usage
  department: Optional[str] = Field(None, max_length=128)
  driver_id: Optional[int] = Field(None, description="ID of assigned driver")
  usage_type: Optional[str] = Field(None, max_length=64)
  
  # Documentation
  logbook_details: Optional[str] = None
  spare_keys_location: Optional[str] = None
  
  # Status
  vehicle_status: Optional[str] = None
  
  # Insurance
  insurance_provider: Optional[str] = Field(None, max_length=128)
  insurance_policy_number: Optional[str] = Field(None, max_length=64)
  insurance_expiry: Optional[str] = None
  
  # Permits and compliance
  permit_details: Optional[str] = None
  
  # Fuel
  fuel_type: Optional[str] = Field(None, max_length=32)
  
  # Tracking
  tracking_device_id: Optional[str] = Field(None, max_length=32)


class PaginatedVehicles(BaseModel):
  total: int
  items: List[Dict[str, Any]]


def _vehicle_to_dict(v: Vehicle) -> Dict[str, Any]:
  d = v.to_dict()
  # Map status enum to string
  d["status"] = v.status.value if hasattr(v.status, "value") else str(v.status)
  d["vehicle_status"] = d["status"]  # Frontend expects vehicle_status
  
  # Map database fields to frontend fields
  if v.model and not d.get("model_name"):
    d["model_name"] = v.model
  if v.vin_number and not d.get("chassis_number"):
    d["chassis_number"] = v.vin_number
  if v.device_imei and not d.get("tracking_device_id"):
    d["tracking_device_id"] = v.device_imei
  if v.current_odometer is not None and not d.get("acquisition_odometer"):
    d["acquisition_odometer"] = v.current_odometer
  
  # Include driver information if assigned
  if v.driver_id:
    d["driver_id"] = v.driver_id
    if v.driver:
      d["driver_name"] = f"{v.driver.first_name} {v.driver.last_name}"
      d["driver_contact"] = v.driver.phone_number
  
  return d


# --------------------
# Endpoints
# --------------------
@router.get("", response_model=PaginatedVehicles, summary="List vehicles")
def list_vehicles(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200), status_filter: Optional[str] = Query(None), make: Optional[str] = Query(None), q: Optional[str] = Query(None)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Vehicle).options(joinedload(Vehicle.driver)).filter(Vehicle.is_deleted.is_(False))
    if status_filter:
      try:
        st = VehicleStatus(status_filter)
        query = query.filter(Vehicle.status == st)
      except Exception:
        raise HTTPException(status_code=400, detail="invalid status filter")
    if make:
      query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if q:
      like = f"%{q}%"
      query = query.filter((Vehicle.vehicle_id.ilike(like)) | (Vehicle.registration_number.ilike(like)) | (Vehicle.model.ilike(like)))
    total = query.count()
    items = query.order_by(Vehicle.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_vehicle_to_dict(v) for v in items]}
  finally:
    session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create vehicle")
def create_vehicle(request: Request, payload: VehicleCreate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    # Check if registration number already exists
    exists = session.query(Vehicle).filter(Vehicle.registration_number == payload.registration_number).one_or_none()
    if exists:
      raise HTTPException(status_code=409, detail="registration_number already exists")
    
    # Auto-generate vehicle_id from registration_number (for the string field)
    vehicle_id_str = payload.registration_number.replace(" ", "").replace("-", "").upper()
    
    # Parse status
    status_value = VehicleStatus.IDLE
    if payload.vehicle_status:
      status_map = {
        "active": VehicleStatus.ACTIVE,
        "idle": VehicleStatus.IDLE,
        "under maintenance": VehicleStatus.MAINTENANCE,
        "decommissioned": VehicleStatus.INACTIVE,
      }
      status_value = status_map.get(payload.vehicle_status.lower(), VehicleStatus.IDLE)
    
    # Create vehicle with all fields
    v = Vehicle(
      vehicle_id=vehicle_id_str,  # String identifier
      registration_number=payload.registration_number,
      make=payload.make,
      model=payload.model_name,  # Map model_name to model
      model_name=payload.model_name,
      year=2024,  # Default year since not provided by frontend
      vin_number=payload.chassis_number,  # Map chassis_number to vin_number
      current_odometer=payload.acquisition_odometer or 0.0,
      max_load_weight=payload.max_load_weight,
      driver_id=payload.driver_id,  # Assign driver
      status=status_value,
      device_imei=payload.tracking_device_id,
    )
    session.add(v)
    session.commit()
    session.refresh(v)  # Refresh to get the auto-generated id
    return _vehicle_to_dict(v)
  finally:
    session.close()


@router.get("/{vehicle_id}", summary="Get vehicle details")
def get_vehicle(request: Request, vehicle_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    v = session.query(Vehicle).options(joinedload(Vehicle.driver)).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    if not v:
      raise HTTPException(status_code=404, detail="vehicle not found")
    return _vehicle_to_dict(v)
  finally:
    session.close()


@router.put("/{vehicle_id}", summary="Update vehicle")
def update_vehicle(request: Request, vehicle_id: int, payload: VehicleUpdate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    v = session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    if not v:
      raise HTTPException(status_code=404, detail="vehicle not found")
    
    # Map frontend fields to database fields
    for field, value in payload.model_dump(exclude_unset=True).items():
      if value is None:
        continue
        
      # Handle status mapping
      if field == "vehicle_status":
        status_map = {
          "active": VehicleStatus.ACTIVE,
          "idle": VehicleStatus.IDLE,
          "under maintenance": VehicleStatus.MAINTENANCE,
          "decommissioned": VehicleStatus.INACTIVE,
        }
        status_value = status_map.get(value.lower(), VehicleStatus.IDLE)
        setattr(v, "status", status_value)
      
      # Map model_name to model
      elif field == "model_name":
        setattr(v, "model", value)
        setattr(v, "model_name", value)
      
      # Map chassis_number to vin_number
      elif field == "chassis_number":
        setattr(v, "vin_number", value)
      
      # Map tracking_device_id to device_imei
      elif field == "tracking_device_id":
        setattr(v, "device_imei", value)
      
      # Handle driver_id assignment
      elif field == "driver_id":
        setattr(v, "driver_id", value)
      
      # Direct field mapping for fields that exist in database
      elif hasattr(v, field):
        setattr(v, field, value)
    
    session.add(v)
    session.commit()
    return _vehicle_to_dict(v)
  finally:
    session.close()


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete vehicle")
def delete_vehicle(request: Request, vehicle_id: int):
  require_roles(dict(request.headers), "admin")
  session = get_session()
  try:
    v = session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    if not v:
      raise HTTPException(status_code=404, detail="vehicle not found")
    v.is_deleted = True
    session.add(v)
    session.commit()
    return
  finally:
    session.close()


@router.get("/{vehicle_id}/telemetry", summary="Get latest telemetry")
def latest_telemetry(request: Request, vehicle_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    t = (
      session.query(Telemetry)
      .filter(Telemetry.vehicle_id == vehicle_id)
      .order_by(Telemetry.timestamp_utc.desc())
      .first()
    )
    if not t:
      raise HTTPException(status_code=404, detail="no telemetry")
    return t.to_dict()
  finally:
    session.close()


@router.get("/{vehicle_id}/location", summary="Get current location")
def current_location(request: Request, vehicle_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    t = (
      session.query(Telemetry)
      .filter(Telemetry.vehicle_id == vehicle_id)
      .order_by(Telemetry.timestamp_utc.desc())
      .first()
    )
    if not t or t.latitude is None or t.longitude is None:
      raise HTTPException(status_code=404, detail="location not available")
    return {"lat": t.latitude, "lon": t.longitude, "alt_m": t.altitude_m, "speed_kph": t.speed_kph, "heading_deg": t.heading_deg}
  finally:
    session.close()


@router.get("/{vehicle_id}/trips", summary="Get trip history")
def trip_history(request: Request, vehicle_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Trip).filter(Trip.vehicle_id == vehicle_id)
    total = query.count()
    items = query.order_by(Trip.start_time_utc.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [t.to_dict() for t in items]}
  finally:
    session.close()


@router.get("/{vehicle_id}/alerts", summary="Get vehicle alerts")
def vehicle_alerts(request: Request, vehicle_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Alert).filter(Alert.vehicle_id == vehicle_id, Alert.is_deleted.is_(False))
    total = query.count()
    items = query.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [a.to_dict() for a in items]}
  finally:
    session.close()

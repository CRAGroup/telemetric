"""Driver management endpoints.

FastAPI router providing:
- CRUD operations for drivers
- Score, behavior events, trips, performance
- Assign vehicle to driver
- Comparison endpoints
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.driver import Driver
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.models.trip import Trip
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.services.analytics.driver_scoring import DriverScoringService
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/drivers", tags=["drivers"])


# --------------------
# Schemas
# --------------------
class DriverCreate(BaseModel):
  # Core identifiers - driver_identifier auto-generated from license_number
  first_name: str = Field(..., min_length=1, max_length=64)
  last_name: str = Field(..., min_length=1, max_length=64)
  
  # Contact
  email: Optional[str] = Field(None, max_length=120)
  phone: Optional[str] = Field(None, max_length=32)
  
  # License
  license_number: str = Field(..., min_length=5, max_length=64)
  license_expiry: Optional[str] = None
  license_class: Optional[str] = Field(None, max_length=10)
  
  # Personal
  national_id: Optional[str] = Field(None, max_length=64)
  date_of_birth: Optional[str] = None
  blood_group: Optional[str] = Field(None, max_length=10)
  
  # Address
  address: Optional[str] = None
  
  # Medical and PSV
  medical_certificate_expiry: Optional[str] = None
  psv_badge_number: Optional[str] = Field(None, max_length=64)
  psv_badge_expiry: Optional[str] = None
  
  # Emergency contacts
  emergency_contact_name: Optional[str] = Field(None, max_length=128)
  emergency_contact_phone: Optional[str] = Field(None, max_length=32)
  
  # Next of kin
  next_of_kin_name: Optional[str] = Field(None, max_length=128)
  next_of_kin_phone: Optional[str] = Field(None, max_length=32)
  next_of_kin_relationship: Optional[str] = Field(None, max_length=64)
  
  # Experience
  years_experience: Optional[int] = None
  previous_employer: Optional[str] = Field(None, max_length=256)
  
  # Status
  status: Optional[str] = Field("active", max_length=20)
  
  # Media
  avatar_url: Optional[str] = None


class DriverUpdate(BaseModel):
  first_name: Optional[str] = Field(None, min_length=1, max_length=64)
  last_name: Optional[str] = Field(None, min_length=1, max_length=64)
  email: Optional[str] = Field(None, max_length=120)
  phone: Optional[str] = Field(None, max_length=32)
  license_number: Optional[str] = Field(None, min_length=5, max_length=64)
  license_expiry: Optional[str] = None
  license_class: Optional[str] = Field(None, max_length=10)
  national_id: Optional[str] = Field(None, max_length=64)
  date_of_birth: Optional[str] = None
  blood_group: Optional[str] = Field(None, max_length=10)
  address: Optional[str] = None
  medical_certificate_expiry: Optional[str] = None
  psv_badge_number: Optional[str] = Field(None, max_length=64)
  psv_badge_expiry: Optional[str] = None
  emergency_contact_name: Optional[str] = Field(None, max_length=128)
  emergency_contact_phone: Optional[str] = Field(None, max_length=32)
  next_of_kin_name: Optional[str] = Field(None, max_length=128)
  next_of_kin_phone: Optional[str] = Field(None, max_length=32)
  next_of_kin_relationship: Optional[str] = Field(None, max_length=64)
  years_experience: Optional[int] = None
  previous_employer: Optional[str] = Field(None, max_length=256)
  status: Optional[str] = Field(None, max_length=20)
  avatar_url: Optional[str] = None


# --------------------
# Helpers
# --------------------

def _driver_to_dict(d: Driver) -> Dict[str, Any]:
  result = d.to_dict()
  # Map backend fields to frontend expected fields
  result["phone"] = d.phone_number  # Map phone_number -> phone
  result["name"] = f"{d.first_name} {d.last_name}"  # Combine first and last name
  return result


# --------------------
# Endpoints
# --------------------
@router.get("", summary="List drivers")
def list_drivers(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200), q: Optional[str] = Query(None)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Driver).filter(Driver.is_deleted.is_(False))
    if q:
      like = f"%{q}%"
      query = query.filter((Driver.first_name.ilike(like)) | (Driver.last_name.ilike(like)) | (Driver.driver_identifier.ilike(like)))
    total = query.count()
    items = query.order_by(Driver.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [_driver_to_dict(d) for d in items]}
  finally:
    session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create driver")
def create_driver(request: Request, payload: DriverCreate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    # Check if license number already exists
    exists = session.query(Driver).filter(Driver.license_number == payload.license_number).one_or_none()
    if exists:
      raise HTTPException(status_code=409, detail="license_number already exists")
    
    # Auto-generate driver_identifier from license_number
    driver_identifier = payload.license_number.replace(" ", "").replace("-", "").upper()
    
    # Map frontend field names to backend field names
    d = Driver(
      driver_identifier=driver_identifier,
      first_name=payload.first_name,
      last_name=payload.last_name,
      license_number=payload.license_number,
      license_expiry=payload.license_expiry,
      license_class=payload.license_class,
      phone_number=payload.phone,  # Map phone -> phone_number
      email=payload.email,
      national_id=payload.national_id,
      date_of_birth=payload.date_of_birth,
      blood_group=payload.blood_group,
      address=payload.address,
      medical_certificate_expiry=payload.medical_certificate_expiry,
      psv_badge_number=payload.psv_badge_number,
      psv_badge_expiry=payload.psv_badge_expiry,
      emergency_contact_name=payload.emergency_contact_name,
      emergency_contact_phone=payload.emergency_contact_phone,
      next_of_kin_name=payload.next_of_kin_name,
      next_of_kin_phone=payload.next_of_kin_phone,
      next_of_kin_relationship=payload.next_of_kin_relationship,
      years_experience=payload.years_experience,
      previous_employer=payload.previous_employer,
      status=payload.status or "active",
      avatar_url=payload.avatar_url,
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    return _driver_to_dict(d)
  finally:
    session.close()


@router.get("/{driver_id}", summary="Get driver details")
def get_driver(request: Request, driver_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    d = session.query(Driver).filter(Driver.id == driver_id, Driver.is_deleted.is_(False)).one_or_none()
    if not d:
      raise HTTPException(status_code=404, detail="driver not found")
    return _driver_to_dict(d)
  finally:
    session.close()


@router.put("/{driver_id}", summary="Update driver")
def update_driver(request: Request, driver_id: int, payload: DriverUpdate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    d = session.query(Driver).filter(Driver.id == driver_id, Driver.is_deleted.is_(False)).one_or_none()
    if not d:
      raise HTTPException(status_code=404, detail="driver not found")
    
    # Map frontend fields to backend fields
    for field, value in payload.model_dump(exclude_unset=True).items():
      if value is None:
        continue
      
      # Map phone -> phone_number
      if field == "phone":
        setattr(d, "phone_number", value)
      # Direct field mapping for fields that exist in database
      elif hasattr(d, field):
        setattr(d, field, value)
    
    session.add(d)
    session.commit()
    return _driver_to_dict(d)
  finally:
    session.close()


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete driver")
def delete_driver(request: Request, driver_id: int):
  require_roles(dict(request.headers), "admin")
  session = get_session()
  try:
    d = session.query(Driver).filter(Driver.id == driver_id, Driver.is_deleted.is_(False)).one_or_none()
    if not d:
      raise HTTPException(status_code=404, detail="driver not found")
    d.is_deleted = True
    session.add(d)
    session.commit()
    return
  finally:
    session.close()


@router.get("/{driver_id}/score", summary="Get driver score")
def driver_score(request: Request, driver_id: int):
  _ = authenticate_request(dict(request.headers))
  svc = DriverScoringService()
  result = svc.compute_scores(driver_id)
  return result


@router.get("/{driver_id}/behavior", summary="Get driver behavior events")
def driver_behavior(request: Request, driver_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Telemetry).filter(Telemetry.driver_id == driver_id)
    total = query.count()
    items = query.order_by(Telemetry.timestamp_utc.desc()).offset((page - 1) * page_size).limit(page_size).all()
    # project only behavior flags and timestamp
    out = []
    for t in items:
      out.append({
        "timestamp_utc": t.timestamp_utc,
        "harsh_accel": t.harsh_accel,
        "hard_brake": t.hard_brake,
        "sharp_corner": t.sharp_corner,
        "speeding": t.speeding,
        "seatbelt_used": t.seatbelt_used,
      })
    return {"total": total, "items": out}
  finally:
    session.close()


@router.get("/{driver_id}/trips", summary="Get driver trip history")
def driver_trips(request: Request, driver_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Trip).filter(Trip.driver_id == driver_id)
    total = query.count()
    items = query.order_by(Trip.start_time_utc.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [t.to_dict() for t in items]}
  finally:
    session.close()


@router.get("/{driver_id}/performance", summary="Get driver performance metrics")
def driver_performance(request: Request, driver_id: int):
  _ = authenticate_request(dict(request.headers))
  # Simple aggregate metrics for demo
  session = get_session()
  try:
    q = session.query(Telemetry).filter(Telemetry.driver_id == driver_id)
    cnt = q.count()
    speeds = [t.speed_kph or 0 for t in q.limit(1000).all()]
    avg_speed = (sum(speeds) / len(speeds)) if speeds else 0.0
    return {"samples": cnt, "avg_speed_kph": avg_speed}
  finally:
    session.close()


@router.put("/{driver_id}/assign-vehicle", summary="Assign vehicle to driver")
def assign_vehicle(request: Request, driver_id: int, vehicle_id: int):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    d = session.query(Driver).filter(Driver.id == driver_id, Driver.is_deleted.is_(False)).one_or_none()
    if not d:
      raise HTTPException(status_code=404, detail="driver not found")
    v = session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    if not v:
      raise HTTPException(status_code=404, detail="vehicle not found")
    v.driver_id = d.id
    session.add(v)
    session.commit()
    return {"status": "assigned", "vehicle_id": v.id, "driver_id": d.id}
  finally:
    session.close()


@router.get("/compare", summary="Compare drivers")
def compare_drivers(request: Request, ids: List[int] = Query(...)):
  _ = authenticate_request(dict(request.headers))
  svc = DriverScoringService()
  out: List[Dict[str, Any]] = []
  for i in ids:
    out.append(svc.compute_scores(i))
  return {"drivers": out}

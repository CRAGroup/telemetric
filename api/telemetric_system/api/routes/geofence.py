"""Geofencing management and violation endpoints.

Provides:
- CRUD for geofences
- Assign/unassign vehicles
- List/query geofences and memberships
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.geofence import Geofence
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.api.middleware.auth import authenticate_request, require_roles


router = APIRouter(prefix="/geofences", tags=["geofences"])


class GeofenceCreate(BaseModel):
  name: str = Field(..., min_length=3, max_length=128)
  description: Optional[str] = Field(None, max_length=512)
  center_lat: float
  center_lng: float
  radius_m: float = Field(..., gt=0)


class GeofenceUpdate(BaseModel):
  description: Optional[str] = Field(None, max_length=512)
  center_lat: Optional[float] = None
  center_lng: Optional[float] = None
  radius_m: Optional[float] = Field(None, gt=0)


@router.get("", summary="List geofences")
def list_geofences(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200), q: Optional[str] = Query(None)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Geofence).filter(Geofence.is_deleted.is_(False))
    if q:
      like = f"%{q}%"
      query = query.filter(Geofence.name.ilike(like))
    total = query.count()
    items = query.order_by(Geofence.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [g.to_dict() for g in items]}
  finally:
    session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create geofence")
def create_geofence(request: Request, payload: GeofenceCreate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    exists = session.query(Geofence).filter(Geofence.name == payload.name).one_or_none()
    if exists:
      raise HTTPException(status_code=409, detail="geofence name exists")
    g = Geofence(
      name=payload.name,
      description=payload.description,
      center_lat=payload.center_lat,
      center_lng=payload.center_lng,
      radius_m=payload.radius_m,
    )
    session.add(g)
    session.commit()
    return g.to_dict()
  finally:
    session.close()


@router.get("/{geofence_id}", summary="Get geofence")
def get_geofence(request: Request, geofence_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    g = session.query(Geofence).filter(Geofence.id == geofence_id, Geofence.is_deleted.is_(False)).one_or_none()
    if not g:
      raise HTTPException(status_code=404, detail="geofence not found")
    return g.to_dict()
  finally:
    session.close()


@router.put("/{geofence_id}", summary="Update geofence")
def update_geofence(request: Request, geofence_id: int, payload: GeofenceUpdate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    g = session.query(Geofence).filter(Geofence.id == geofence_id, Geofence.is_deleted.is_(False)).one_or_none()
    if not g:
      raise HTTPException(status_code=404, detail="geofence not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
      setattr(g, k, v)
    session.add(g)
    session.commit()
    return g.to_dict()
  finally:
    session.close()


@router.delete("/{geofence_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete geofence")
def delete_geofence(request: Request, geofence_id: int):
  require_roles(dict(request.headers), "admin")
  session = get_session()
  try:
    g = session.query(Geofence).filter(Geofence.id == geofence_id, Geofence.is_deleted.is_(False)).one_or_none()
    if not g:
      raise HTTPException(status_code=404, detail="geofence not found")
    g.is_deleted = True
    session.add(g)
    session.commit()
    return
  finally:
    session.close()


@router.put("/{geofence_id}/assign", summary="Assign vehicle to geofence")
def assign_vehicle(request: Request, geofence_id: int, vehicle_id: int):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    g = session.query(Geofence).filter(Geofence.id == geofence_id, Geofence.is_deleted.is_(False)).one_or_none()
    if not g:
      raise HTTPException(status_code=404, detail="geofence not found")
    v = session.query(Vehicle).filter(Vehicle.id == vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    if not v:
      raise HTTPException(status_code=404, detail="vehicle not found")
    g.vehicles.append(v)
    session.add(g)
    session.commit()
    return {"status": "assigned", "geofence_id": g.id, "vehicle_id": v.id}
  finally:
    session.close()


@router.put("/{geofence_id}/unassign", summary="Unassign vehicle from geofence")
def unassign_vehicle(request: Request, geofence_id: int, vehicle_id: int):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    g = session.query(Geofence).filter(Geofence.id == geofence_id, Geofence.is_deleted.is_(False)).one_or_none()
    if not g:
      raise HTTPException(status_code=404, detail="geofence not found")
    g.vehicles = [v for v in g.vehicles if v.id != vehicle_id]
    session.add(g)
    session.commit()
    return {"status": "unassigned", "geofence_id": g.id, "vehicle_id": vehicle_id}
  finally:
    session.close()


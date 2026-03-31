"""Vehicle Types CRUD endpoints.

FastAPI router providing:
- List/create/get/update/delete vehicle types
- Compatible with Supabase frontend
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.vehicle_type import VehicleType
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/vehicle-types", tags=["vehicle-types"])


# Schemas
class VehicleTypeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=128)
    description: Optional[str] = None


class VehicleTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128)
    description: Optional[str] = None


# Endpoints
@router.get("", summary="List vehicle types")
def list_vehicle_types(request: Request, page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=200)):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        query = session.query(VehicleType).filter(VehicleType.is_deleted.is_(False))
        total = query.count()
        items = query.order_by(VehicleType.name).offset((page - 1) * page_size).limit(page_size).all()
        return {"total": total, "items": [vt.to_dict() for vt in items]}
    finally:
        session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create vehicle type")
def create_vehicle_type(request: Request, payload: VehicleTypeCreate):
    require_roles(dict(request.headers), "admin", "manager")
    session = get_session()
    try:
        exists = session.query(VehicleType).filter(VehicleType.name == payload.name).one_or_none()
        if exists:
            raise HTTPException(status_code=409, detail="vehicle type already exists")
        
        vt = VehicleType(name=payload.name, description=payload.description)
        session.add(vt)
        session.commit()
        return vt.to_dict()
    finally:
        session.close()


@router.get("/{type_id}", summary="Get vehicle type")
def get_vehicle_type(request: Request, type_id: int):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        vt = session.query(VehicleType).filter(VehicleType.id == type_id, VehicleType.is_deleted.is_(False)).one_or_none()
        if not vt:
            raise HTTPException(status_code=404, detail="vehicle type not found")
        return vt.to_dict()
    finally:
        session.close()


@router.put("/{type_id}", summary="Update vehicle type")
def update_vehicle_type(request: Request, type_id: int, payload: VehicleTypeUpdate):
    require_roles(dict(request.headers), "admin", "manager")
    session = get_session()
    try:
        vt = session.query(VehicleType).filter(VehicleType.id == type_id, VehicleType.is_deleted.is_(False)).one_or_none()
        if not vt:
            raise HTTPException(status_code=404, detail="vehicle type not found")
        
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(vt, field, value)
        
        session.add(vt)
        session.commit()
        return vt.to_dict()
    finally:
        session.close()


@router.delete("/{type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete vehicle type")
def delete_vehicle_type(request: Request, type_id: int):
    require_roles(dict(request.headers), "admin")
    session = get_session()
    try:
        vt = session.query(VehicleType).filter(VehicleType.id == type_id, VehicleType.is_deleted.is_(False)).one_or_none()
        if not vt:
            raise HTTPException(status_code=404, detail="vehicle type not found")
        
        vt.is_deleted = True
        session.add(vt)
        session.commit()
        return
    finally:
        session.close()

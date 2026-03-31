"""Maintenance records endpoints.

FastAPI router providing:
- List/create/get/update/delete maintenance records
- Filter by vehicle, status, date range
- Stats summary
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.maintenance import MaintenanceRecord
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


class MaintenanceCreate(BaseModel):
    vehicle_id: int
    service_type: str = Field(..., min_length=2, max_length=64)
    description: Optional[str] = Field(None, max_length=500)
    service_date: str  # ISO date string
    odometer_km: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    mechanic: Optional[str] = Field(None, max_length=128)
    priority: Optional[str] = Field("medium", max_length=20)
    record_type: Optional[str] = Field("scheduled", max_length=20)
    status: Optional[str] = Field("pending", max_length=20)


class MaintenanceUpdate(BaseModel):
    service_type: Optional[str] = Field(None, min_length=2, max_length=64)
    description: Optional[str] = Field(None, max_length=500)
    service_date: Optional[str] = None
    odometer_km: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    mechanic: Optional[str] = Field(None, max_length=128)
    priority: Optional[str] = Field(None, max_length=20)
    record_type: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, max_length=20)
    completed_date: Optional[str] = None


def _record_to_dict(r: MaintenanceRecord, vehicle: Optional[Vehicle] = None) -> Dict[str, Any]:
    d = r.to_dict()
    # Add vehicle info
    if vehicle:
        d["vehicle_name"] = f"{vehicle.registration_number} - {vehicle.make} {vehicle.model or ''}"
        d["vehicle_registration"] = vehicle.registration_number
    # Ensure frontend-expected fields
    d["type"] = d.get("record_type", "scheduled")
    d["scheduledDate"] = str(d.get("service_date", ""))
    d["completedDate"] = d.get("completed_date")
    d["mechanic"] = d.get("mechanic")
    d["priority"] = d.get("priority", "medium")
    return d


@router.get("", summary="List maintenance records")
def list_maintenance(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    vehicle_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        query = session.query(MaintenanceRecord).filter(MaintenanceRecord.is_deleted.is_(False))
        if vehicle_id:
            query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
        if status_filter:
            query = query.filter(MaintenanceRecord.status == status_filter)
        if q:
            like = f"%{q}%"
            query = query.filter(
                (MaintenanceRecord.service_type.ilike(like)) |
                (MaintenanceRecord.description.ilike(like))
            )
        total = query.count()
        items = query.order_by(MaintenanceRecord.service_date.desc()).offset((page - 1) * page_size).limit(page_size).all()

        # Fetch vehicles for enrichment
        vehicle_ids = list({r.vehicle_id for r in items})
        vehicles = {v.id: v for v in session.query(Vehicle).filter(Vehicle.id.in_(vehicle_ids)).all()}

        return {"total": total, "items": [_record_to_dict(r, vehicles.get(r.vehicle_id)) for r in items]}
    finally:
        session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create maintenance record")
def create_maintenance(request: Request, payload: MaintenanceCreate):
    require_roles(dict(request.headers), "admin", "manager")
    session = get_session()
    try:
        # Validate vehicle exists
        v = session.query(Vehicle).filter(Vehicle.id == payload.vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
        if not v:
            raise HTTPException(status_code=404, detail="vehicle not found")

        svc_date = date.fromisoformat(payload.service_date)
        r = MaintenanceRecord(
            vehicle_id=payload.vehicle_id,
            service_type=payload.service_type,
            description=payload.description,
            service_date=svc_date,
            odometer_km=payload.odometer_km,
            cost=payload.cost,
            mechanic=payload.mechanic,
            priority=payload.priority or "medium",
            record_type=payload.record_type or "scheduled",
            status=payload.status or "pending",
        )
        session.add(r)
        session.commit()
        session.refresh(r)
        return _record_to_dict(r, v)
    finally:
        session.close()


@router.get("/stats", summary="Maintenance statistics")
def maintenance_stats(request: Request):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        base = session.query(MaintenanceRecord).filter(MaintenanceRecord.is_deleted.is_(False))
        total = base.count()
        pending = base.filter(MaintenanceRecord.status == "pending").count()
        in_progress = base.filter(MaintenanceRecord.status == "in_progress").count()
        overdue = base.filter(MaintenanceRecord.status == "overdue").count()
        completed = base.filter(MaintenanceRecord.status == "completed").count()
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "overdue": overdue,
            "completed": completed,
        }
    finally:
        session.close()


@router.get("/{record_id}", summary="Get maintenance record")
def get_maintenance(request: Request, record_id: int):
    _ = authenticate_request(dict(request.headers))
    session = get_session()
    try:
        r = session.query(MaintenanceRecord).filter(
            MaintenanceRecord.id == record_id,
            MaintenanceRecord.is_deleted.is_(False)
        ).one_or_none()
        if not r:
            raise HTTPException(status_code=404, detail="record not found")
        v = session.query(Vehicle).filter(Vehicle.id == r.vehicle_id).one_or_none()
        return _record_to_dict(r, v)
    finally:
        session.close()


@router.put("/{record_id}", summary="Update maintenance record")
def update_maintenance(request: Request, record_id: int, payload: MaintenanceUpdate):
    require_roles(dict(request.headers), "admin", "manager")
    session = get_session()
    try:
        r = session.query(MaintenanceRecord).filter(
            MaintenanceRecord.id == record_id,
            MaintenanceRecord.is_deleted.is_(False)
        ).one_or_none()
        if not r:
            raise HTTPException(status_code=404, detail="record not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            if field == "service_date":
                setattr(r, field, date.fromisoformat(value))
            elif field == "completed_date":
                setattr(r, field, date.fromisoformat(value) if value else None)
            elif hasattr(r, field):
                setattr(r, field, value)

        session.add(r)
        session.commit()
        v = session.query(Vehicle).filter(Vehicle.id == r.vehicle_id).one_or_none()
        return _record_to_dict(r, v)
    finally:
        session.close()


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete maintenance record")
def delete_maintenance(request: Request, record_id: int):
    require_roles(dict(request.headers), "admin")
    session = get_session()
    try:
        r = session.query(MaintenanceRecord).filter(
            MaintenanceRecord.id == record_id,
            MaintenanceRecord.is_deleted.is_(False)
        ).one_or_none()
        if not r:
            raise HTTPException(status_code=404, detail="record not found")
        r.is_deleted = True
        session.add(r)
        session.commit()
        return
    finally:
        session.close()

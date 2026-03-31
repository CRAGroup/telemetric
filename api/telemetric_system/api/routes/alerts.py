"""Alert endpoints for rules, querying, and acknowledgements.

Provides:
- CRUD for alerts (soft-delete)
- Acknowledge/unacknowledge
- List/query with pagination and filters
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.alert import Alert, AlertSeverity
from telemetric_system.api.middleware.auth import authenticate_request, require_roles


router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
  vehicle_id: int
  driver_id: Optional[int] = None
  alert_type: str = Field(..., min_length=2, max_length=64)
  message: Optional[str] = Field(None, max_length=500)
  severity: str = Field("warning")
  rule_id: Optional[str] = Field(None, max_length=64)


class AlertUpdate(BaseModel):
  message: Optional[str] = Field(None, max_length=500)
  severity: Optional[str] = None
  acknowledged: Optional[bool] = None


@router.get("", summary="List alerts")
def list_alerts(request: Request, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200), vehicle_id: Optional[int] = Query(None), severity: Optional[str] = Query(None)):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    query = session.query(Alert).filter(Alert.is_deleted.is_(False))
    if vehicle_id:
      query = query.filter(Alert.vehicle_id == vehicle_id)
    if severity:
      query = query.filter(Alert.severity == severity)
    total = query.count()
    items = query.order_by(Alert.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": [a.to_dict() for a in items]}
  finally:
    session.close()


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create alert")
def create_alert(request: Request, payload: AlertCreate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    sev = payload.severity or AlertSeverity.WARNING.value
    a = Alert(
      vehicle_id=payload.vehicle_id,
      driver_id=payload.driver_id,
      alert_type=payload.alert_type,
      message=payload.message,
      severity=sev,
      rule_id=payload.rule_id,
    )
    session.add(a)
    session.commit()
    return a.to_dict()
  finally:
    session.close()


@router.get("/{alert_id}", summary="Get alert")
def get_alert(request: Request, alert_id: int):
  _ = authenticate_request(dict(request.headers))
  session = get_session()
  try:
    a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
    if not a:
      raise HTTPException(status_code=404, detail="alert not found")
    return a.to_dict()
  finally:
    session.close()


@router.put("/{alert_id}", summary="Update alert")
def update_alert(request: Request, alert_id: int, payload: AlertUpdate):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
    if not a:
      raise HTTPException(status_code=404, detail="alert not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
      setattr(a, k, v)
    session.add(a)
    session.commit()
    return a.to_dict()
  finally:
    session.close()


@router.post("/{alert_id}/ack", summary="Acknowledge alert")
def acknowledge_alert(request: Request, alert_id: int):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
    if not a:
      raise HTTPException(status_code=404, detail="alert not found")
    a.acknowledged = True
    a.acknowledged_at = datetime.utcnow()
    session.add(a)
    session.commit()
    return {"status": "acknowledged"}
  finally:
    session.close()


@router.post("/{alert_id}/unack", summary="Unacknowledge alert")
def unacknowledge_alert(request: Request, alert_id: int):
  require_roles(dict(request.headers), "admin", "manager")
  session = get_session()
  try:
    a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
    if not a:
      raise HTTPException(status_code=404, detail="alert not found")
    a.acknowledged = False
    a.acknowledged_at = None
    session.add(a)
    session.commit()
    return {"status": "unacknowledged"}
  finally:
    session.close()


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Soft delete alert")
def delete_alert(request: Request, alert_id: int):
  require_roles(dict(request.headers), "admin")
  session = get_session()
  try:
    a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
    if not a:
      raise HTTPException(status_code=404, detail="alert not found")
    a.is_deleted = True
    session.add(a)
    session.commit()
    return
  finally:
    session.close()


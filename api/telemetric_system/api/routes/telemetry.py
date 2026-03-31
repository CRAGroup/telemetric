"""Telemetry data endpoints.

FastAPI router providing:
- POST /telemetry: ingest telemetry from devices (API key or JWT)
- GET /telemetry/live: live stream placeholder (delegate to WebSocket service)
- GET /telemetry/history: query historical telemetry with time range and aggregation
- GET /telemetry/export: export telemetry data as CSV
"""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.api.middleware.auth import authenticate_request

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


# --------------------
# Schemas
# --------------------
class TelemetryIngest(BaseModel):
  vehicle_id: Optional[int] = Field(None, description="DB vehicle id")
  vehicle_identifier: Optional[str] = Field(None, description="External vehicle identifier, e.g., VH-0001")
  timestamp: Optional[float] = Field(None, description="Unix epoch seconds; server will use now if omitted")
  vehicle: Dict[str, Any] = Field(default_factory=dict)
  engine: Dict[str, Any] = Field(default_factory=dict)


class HistoryQuery(BaseModel):
  start: Optional[datetime] = None
  end: Optional[datetime] = None
  vehicle_ids: Optional[List[int]] = None
  level: str = Field("raw", description="raw|hour|day")
  limit: int = Field(1000, ge=1, le=10000)
  offset: int = Field(0, ge=0)


def _ensure_auth(request: Request) -> None:
  ctx = authenticate_request(dict(request.headers))
  if not (ctx.user_id or ctx.device_id):
    raise HTTPException(status_code=401, detail="unauthorized")


def _find_vehicle_db_id(session, body: TelemetryIngest) -> Optional[int]:
  if body.vehicle_id:
    v = session.query(Vehicle).filter(Vehicle.id == body.vehicle_id, Vehicle.is_deleted.is_(False)).one_or_none()
    return None if not v else v.id
  if body.vehicle_identifier:
    v = session.query(Vehicle).filter(Vehicle.vehicle_id == body.vehicle_identifier, Vehicle.is_deleted.is_(False)).one_or_none()
    return None if not v else v.id
  return None


# --------------------
# Endpoints
# --------------------
@router.post("", status_code=status.HTTP_202_ACCEPTED, summary="Ingest telemetry")
def post_telemetry(request: Request, payload: TelemetryIngest):
  _ensure_auth(request)
  session = get_session()
  try:
    vid = _find_vehicle_db_id(session, payload)
    if not vid:
      raise HTTPException(status_code=404, detail="vehicle not found")
    ts = datetime.utcfromtimestamp(payload.timestamp) if payload.timestamp else datetime.utcnow()
    v = payload.vehicle or {}
    e = payload.engine or {}
    row = Telemetry(
      vehicle_id=vid,
      driver_id=None,
      timestamp_utc=ts,
      rpm=_num(e.get("rpm")),
      engine_temp_c=_num(e.get("engine_temp_c")),
      oil_pressure_kpa=_num(e.get("oil_pressure_kpa")),
      battery_voltage_v=_num(e.get("battery_voltage_v")),
      throttle_pos_pct=_num(e.get("throttle_pos_pct")),
      engine_load_pct=_num(e.get("engine_load_pct")),
      latitude=_num(v.get("lat")),
      longitude=_num(v.get("lon")),
      speed_kph=_num(v.get("speed_kph")) or _num(v.get("speed_kph_smoothed")),
      heading_deg=_num(v.get("heading_deg")),
      altitude_m=_num(v.get("alt_m")),
      fuel_level_pct=_num(e.get("fuel_level_pct")),
      fuel_rate_lph=_num(e.get("fuel_rate_lph")),
      harsh_accel=None,
      hard_brake=None,
      sharp_corner=None,
      speeding=None,
      seatbelt_used=None,
    )
    session.add(row)
    session.commit()
    return {"status": "accepted"}
  finally:
    session.close()


@router.get("/live", summary="Live telemetry stream (WebSocket placeholder)")
def telemetry_live(request: Request):
  _ensure_auth(request)
  # In this REST router, return info on WebSocket endpoint configured elsewhere
  return {"message": "Use WebSocket endpoint at /ws/telemetry to subscribe to live telemetry."}


@router.get("/history", summary="Query historical telemetry")
def telemetry_history(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None), vehicle_ids: Optional[List[int]] = Query(None), level: str = Query("raw", pattern="^(raw|hour|day)$"), limit: int = Query(1000, ge=1, le=10000), offset: int = Query(0, ge=0)):
  _ensure_auth(request)
  session = get_session()
  try:
    if level == "raw":
      query = session.query(Telemetry)
      if vehicle_ids:
        query = query.filter(Telemetry.vehicle_id.in_(vehicle_ids))
      if start:
        query = query.filter(Telemetry.timestamp_utc >= start)
      if end:
        query = query.filter(Telemetry.timestamp_utc < end)
      total = query.count()
      rows = query.order_by(Telemetry.timestamp_utc.desc()).offset(offset).limit(limit).all()
      return {"total": total, "items": [r.to_dict() for r in rows]}
    # Aggregates (hour/day) via materialized views if present; fallback to 400 if not configured
    view = "telemetry_hourly" if level == "hour" else "telemetry_daily"
    try:
      # raw SQL to aggregate view
      where = []
      params: Dict[str, Any] = {}
      if vehicle_ids:
        where.append("vehicle_id = ANY(:vids)")
        params["vids"] = vehicle_ids
      if start:
        where.append("bucket >= :start")
        params["start"] = start
      if end:
        where.append("bucket < :end")
        params["end"] = end
      w = (" WHERE " + " AND ".join(where)) if where else ""
      sql = f"SELECT bucket, vehicle_id, avg_speed_kph, max_speed_kph, avg_engine_temp_c, avg_fuel_level_pct FROM {view}{w} ORDER BY bucket DESC OFFSET :offset LIMIT :limit"
      params["offset"] = offset
      params["limit"] = limit
      result = session.execute(sql, params)  # type: ignore[arg-type]
      items = []
      for row in result:
        items.append({
          "bucket": row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0]),
          "vehicle_id": row[1],
          "avg_speed_kph": float(row[2] or 0),
          "max_speed_kph": float(row[3] or 0),
          "avg_engine_temp_c": float(row[4] or 0),
          "avg_fuel_level_pct": float(row[5] or 0),
        })
      return {"total": len(items), "items": items}
    except Exception:
      raise HTTPException(status_code=400, detail="aggregate views unavailable")
  finally:
    session.close()


@router.get("/export", summary="Export telemetry as CSV")
def telemetry_export(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None), vehicle_ids: Optional[List[int]] = Query(None), level: str = Query("raw", pattern="^(raw|hour|day)$")):
  _ensure_auth(request)
  session = get_session()
  try:
    headers: List[str]
    rows_out: List[Dict[str, Any]] = []
    if level == "raw":
      query = session.query(Telemetry)
      if vehicle_ids:
        query = query.filter(Telemetry.vehicle_id.in_(vehicle_ids))
      if start:
        query = query.filter(Telemetry.timestamp_utc >= start)
      if end:
        query = query.filter(Telemetry.timestamp_utc < end)
      rows = query.order_by(Telemetry.timestamp_utc.desc()).limit(10000).all()
      for r in rows:
        d = r.to_dict()
        rows_out.append(d)
      headers = list(rows_out[0].keys()) if rows_out else ["id", "timestamp_utc", "vehicle_id"]
    else:
      view = "telemetry_hourly" if level == "hour" else "telemetry_daily"
      try:
        where = []
        params: Dict[str, Any] = {}
        if vehicle_ids:
          where.append("vehicle_id = ANY(:vids)")
          params["vids"] = vehicle_ids
        if start:
          where.append("bucket >= :start")
          params["start"] = start
        if end:
          where.append("bucket < :end")
          params["end"] = end
        w = (" WHERE " + " AND ".join(where)) if where else ""
        sql = f"SELECT bucket, vehicle_id, avg_speed_kph, max_speed_kph, avg_engine_temp_c, avg_fuel_level_pct FROM {view}{w} ORDER BY bucket DESC LIMIT 10000"
        result = session.execute(sql, params)  # type: ignore[arg-type]
        for row in result:
          rows_out.append({
            "bucket": row[0].isoformat() if hasattr(row[0], "isoformat") else str(row[0]),
            "vehicle_id": row[1],
            "avg_speed_kph": float(row[2] or 0),
            "max_speed_kph": float(row[3] or 0),
            "avg_engine_temp_c": float(row[4] or 0),
            "avg_fuel_level_pct": float(row[5] or 0),
          })
        headers = ["bucket", "vehicle_id", "avg_speed_kph", "max_speed_kph", "avg_engine_temp_c", "avg_fuel_level_pct"]
      except Exception:
        raise HTTPException(status_code=400, detail="aggregate views unavailable")

    # Build CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in rows_out:
      writer.writerow({k: row.get(k, "") for k in headers})
    csv_bytes = output.getvalue().encode("utf-8")
    return Response(content=csv_bytes, media_type="text/csv")
  finally:
    session.close()


def _num(value: Any) -> Optional[float]:
  try:
    if value is None:
      return None
    return float(value)
  except Exception:
    return None

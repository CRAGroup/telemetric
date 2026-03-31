"""Report generation endpoints.

Provides:
- POST /reports/generate: generate custom report (CSV stub for now)
- GET /reports/{id}: get report metadata
- GET /reports/{id}/download: download report file
- GET /reports/templates: list available templates
- POST /reports/schedule: schedule recurring reports (stub)
"""

from __future__ import annotations

import csv
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.trip import Trip
from telemetric_system.models.alert import Alert
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.api.middleware.auth import authenticate_request, require_roles

router = APIRouter(prefix="/reports", tags=["reports"])

# In-memory registry for generated reports
_REPORTS: Dict[str, Dict[str, Any]] = {}
_BASE_DIR = Path(__file__).resolve().parents[3] / "static" / "exports"
_BASE_DIR.mkdir(parents=True, exist_ok=True)


class ReportGenerateRequest(BaseModel):
  report_type: str = Field(..., pattern="^(fleet|driver|fuel|maintenance|cost)$", description="fleet|driver|fuel|maintenance|cost")
  format: str = Field("csv", pattern="^(csv|excel|pdf)$")
  start: Optional[datetime] = None
  end: Optional[datetime] = None
  vehicle_ids: Optional[List[int]] = None
  driver_ids: Optional[List[int]] = None
  title: Optional[str] = None


class ReportScheduleRequest(BaseModel):
  report_type: str = Field(..., pattern="^(fleet|driver|fuel|maintenance|cost)$")
  format: str = Field("csv", pattern="^(csv|excel|pdf)$")
  cron: Optional[str] = Field(None, description="cron expression or null for interval")
  interval_minutes: Optional[int] = Field(None, ge=5)
  recipients: List[str] = Field(default_factory=list)


@router.get("/templates", summary="List available report templates")
def list_templates(request: Request):
  _ensure_auth(request)
  return {
    "templates": [
      {"key": "fleet", "name": "Fleet Performance"},
      {"key": "driver", "name": "Driver Behavior"},
      {"key": "fuel", "name": "Fuel Analysis"},
      {"key": "maintenance", "name": "Maintenance"},
      {"key": "cost", "name": "Cost Analysis"},
    ]
  }


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED, summary="Generate report")
def generate_report(request: Request, payload: ReportGenerateRequest):
  require_roles(dict(request.headers), "admin", "manager")
  s, e = _parse_dates(payload.start, payload.end)
  report_id = uuid.uuid4().hex
  file_path = _BASE_DIR / f"report_{report_id}.csv"

  # Build rows based on report type (simple CSV generation)
  headers, rows = _build_report_rows(payload.report_type, s, e, payload.vehicle_ids, payload.driver_ids)

  with file_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for r in rows:
      writer.writerow({k: r.get(k, "") for k in headers})

  _REPORTS[report_id] = {
    "id": report_id,
    "type": payload.report_type,
    "format": payload.format,
    "title": payload.title or f"{payload.report_type.title()} Report",
    "start": s.isoformat(),
    "end": e.isoformat(),
    "path": str(file_path),
    "created_at": datetime.utcnow().isoformat(),
  }
  return {"id": report_id, "status": "generated"}


@router.get("/{report_id}", summary="Get report metadata")
def get_report(request: Request, report_id: str):
  _ensure_auth(request)
  meta = _REPORTS.get(report_id)
  if not meta:
    raise HTTPException(status_code=404, detail="report not found")
  return meta


@router.get("/{report_id}/download", summary="Download report")
def download_report(request: Request, report_id: str):
  _ensure_auth(request)
  meta = _REPORTS.get(report_id)
  if not meta:
    raise HTTPException(status_code=404, detail="report not found")
  path = Path(meta["path"])
  if not path.exists():
    raise HTTPException(status_code=410, detail="report file missing")
  return FileResponse(path, media_type="text/csv", filename=path.name)


@router.post("/schedule", status_code=status.HTTP_202_ACCEPTED, summary="Schedule recurring report")
def schedule_report(request: Request, payload: ReportScheduleRequest):
  require_roles(dict(request.headers), "admin", "manager")
  sched_id = uuid.uuid4().hex
  # Stub: In production, store schedule in DB/Celery beat
  return {"id": sched_id, "status": "scheduled"}


# ------------------------
# Helpers
# ------------------------

def _ensure_auth(request: Request) -> None:
  ctx = authenticate_request(dict(request.headers))
  if not (ctx.user_id or ctx.device_id):
    raise HTTPException(status_code=401, detail="unauthorized")


def _parse_dates(start: Optional[datetime], end: Optional[datetime]) -> tuple[datetime, datetime]:
  e = end or datetime.utcnow()
  s = start or (e - timedelta(days=30))
  return s, e


def _build_report_rows(report_type: str, start: datetime, end: datetime, vehicle_ids: Optional[List[int]], driver_ids: Optional[List[int]]) -> tuple[List[str], List[Dict[str, Any]]]:
  session = get_session()
  try:
    if report_type == "fleet":
      headers = ["vehicle_id", "samples", "avg_speed_kph", "max_speed_kph"]
      rows: List[Dict[str, Any]] = []
      q = session.query(Telemetry.vehicle_id)
      if vehicle_ids:
        q = q.filter(Telemetry.vehicle_id.in_(vehicle_ids))
      vids = {vid for (vid,) in q.distinct().all()}
      for vid in vids:
        t_q = session.query(Telemetry).filter(Telemetry.vehicle_id == vid, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
        samples = t_q.count()
        speeds = [t.speed_kph or 0 for t in t_q.limit(1000).all()]
        rows.append({"vehicle_id": vid, "samples": samples, "avg_speed_kph": round(sum(speeds) / len(speeds), 3) if speeds else 0.0, "max_speed_kph": max(speeds) if speeds else 0.0})
      return headers, rows

    if report_type == "driver":
      headers = ["driver_id", "samples", "avg_speed_kph"]
      rows = []
      dids = driver_ids or [d.id for d in session.query(Telemetry.driver_id).filter(Telemetry.driver_id.isnot(None)).distinct().all()]
      for did in dids:
        t_q = session.query(Telemetry).filter(Telemetry.driver_id == did, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
        samples = t_q.count()
        speeds = [t.speed_kph or 0 for t in t_q.limit(1000).all()]
        rows.append({"driver_id": did, "samples": samples, "avg_speed_kph": round(sum(speeds) / len(speeds), 3) if speeds else 0.0})
      return headers, rows

    if report_type == "fuel":
      headers = ["vehicle_id", "avg_fuel_level_pct"]
      rows = []
      vids = vehicle_ids or [v.id for v in session.query(Vehicle.id).all()]
      for vid in vids:
        avg_fuel = session.execute(
          "SELECT AVG(fuel_level_pct) FROM telemetry_data WHERE vehicle_id = :vid AND timestamp_utc >= :s AND timestamp_utc < :e",
          {"vid": vid, "s": start, "e": end},
        ).scalar()
        rows.append({"vehicle_id": vid, "avg_fuel_level_pct": float(avg_fuel or 0)})
      return headers, rows

    if report_type == "maintenance":
      headers = ["vehicle_id", "num_records", "total_cost"]
      rows = []
      vids = vehicle_ids or [v.id for v in session.query(Vehicle.id).all()]
      for vid in vids:
        total_cost = session.execute(
          "SELECT COALESCE(SUM(cost),0), COUNT(*) FROM maintenance_records WHERE vehicle_id = :vid",
          {"vid": vid},
        ).first()
        rows.append({"vehicle_id": vid, "num_records": int(total_cost[1] or 0), "total_cost": float(total_cost[0] or 0)})
      return headers, rows

    if report_type == "cost":
      headers = ["vehicle_id", "fuel_liters", "maintenance_cost"]
      rows = []
      vids = vehicle_ids or [v.id for v in session.query(Vehicle.id).all()]
      for vid in vids:
        fuel_l = session.execute(
          "SELECT COALESCE(SUM(fuel_used_l),0) FROM trips WHERE vehicle_id = :vid AND start_time_utc >= :s AND start_time_utc < :e",
          {"vid": vid, "s": start, "e": end},
        ).scalar()
        maint_cost = session.execute(
          "SELECT COALESCE(SUM(cost),0) FROM maintenance_records WHERE vehicle_id = :vid",
          {"vid": vid},
        ).scalar()
        rows.append({"vehicle_id": vid, "fuel_liters": float(fuel_l or 0), "maintenance_cost": float(maint_cost or 0)})
      return headers, rows

    return ["message"], [{"message": "Unknown report type"}]
  finally:
    session.close()

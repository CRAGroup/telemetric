"""Analytics endpoints for KPIs and fleet metrics.

Provides endpoints for fleet overview, fuel efficiency, driver rankings, cost
analysis, utilization, and trend analysis, with date ranges and grouping.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from telemetric_system.core.database.connection import get_session
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.trip import Trip
from telemetric_system.models.driver import Driver
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.services.data_processor.batch_processor import BatchProcessor, BatchConfig
from telemetric_system.api.middleware.auth import authenticate_request

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _ensure_auth(request: Request) -> None:
  ctx = authenticate_request(dict(request.headers))
  if not (ctx.user_id or ctx.device_id):
    raise HTTPException(status_code=401, detail="unauthorized")


def _parse_dates(start: Optional[datetime], end: Optional[datetime]) -> tuple[datetime, datetime]:
  e = end or datetime.utcnow()
  s = start or (e - timedelta(days=30))
  return s, e


@router.get("/fleet-overview", summary="Fleet summary")
def fleet_overview(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None)):
  _ensure_auth(request)
  session = get_session()
  try:
    s, e = _parse_dates(start, end)
    total_vehicles = session.query(Vehicle).filter(Vehicle.is_deleted.is_(False)).count()
    active_vehicles = session.query(Vehicle).filter(Vehicle.is_deleted.is_(False), Vehicle.status != "inactive").count()
    telem_count = session.query(Telemetry).filter(Telemetry.timestamp_utc >= s, Telemetry.timestamp_utc < e).count()
    trip_count = session.query(Trip).filter(Trip.start_time_utc >= s, Trip.start_time_utc < e).count()
    return {"vehicles": {"total": total_vehicles, "active": active_vehicles}, "telemetry": telem_count, "trips": trip_count}
  finally:
    session.close()


@router.get("/fuel-efficiency", summary="Fuel metrics")
def fuel_efficiency(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None)):
  _ensure_auth(request)
  s, e = _parse_dates(start, end)
  bp = BatchProcessor(BatchConfig(lookback_days=max(1, (e - s).days)))
  data = bp.run()
  return {"fuel_metrics": data.get("fuel_metrics", [])}


@router.get("/driver-rankings", summary="Driver leaderboard")
def driver_rankings(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None)):
  _ensure_auth(request)
  s, e = _parse_dates(start, end)
  session = get_session()
  try:
    # Rank by average speed below limit and fewer infractions
    q = (
      session.query(Driver.id, Driver.first_name, Driver.last_name)
      .filter(Driver.is_deleted.is_(False))
    )
    drivers = q.all()
    rankings: List[Dict[str, Any]] = []
    for d in drivers:
      speeds = [t.speed_kph or 0 for t in session.query(Telemetry).filter(Telemetry.driver_id == d.id, Telemetry.timestamp_utc >= s, Telemetry.timestamp_utc < e).limit(1000).all()]
      avg_speed = (sum(speeds) / len(speeds)) if speeds else 0.0
      infractions = session.query(Telemetry).filter(Telemetry.driver_id == d.id, Telemetry.speed_kph.isnot(None), Telemetry.speed_kph > 120.0, Telemetry.timestamp_utc >= s, Telemetry.timestamp_utc < e).count()
      score = max(0.0, 100.0 - infractions * 5 - max(0.0, avg_speed - 80.0))
      rankings.append({"driver_id": d.id, "name": f"{d.first_name} {d.last_name}", "score": round(score, 2)})
    rankings.sort(key=lambda x: x["score"], reverse=True)
    return {"rankings": rankings}
  finally:
    session.close()


@router.get("/cost-analysis", summary="Cost breakdown")
def cost_analysis(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None)):
  _ensure_auth(request)
  # Placeholder: derive from trips and maintenance
  s, e = _parse_dates(start, end)
  session = get_session()
  try:
    maint = session.execute("SELECT COALESCE(SUM(cost),0) FROM maintenance_records").scalar() or 0.0
    trips = session.execute("SELECT COALESCE(SUM(fuel_used_l),0) FROM trips WHERE start_time_utc >= :s AND start_time_utc < :e", {"s": s, "e": e}).scalar() or 0.0
    return {"maintenance_cost": float(maint), "fuel_liters": float(trips)}
  finally:
    session.close()


@router.get("/utilization", summary="Vehicle utilization")
def utilization(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None)):
  _ensure_auth(request)
  s, e = _parse_dates(start, end)
  session = get_session()
  try:
    # Utilization heuristic: fraction of samples with speed > 0 by vehicle
    rows = (
      session.execute(
        """
        SELECT vehicle_id,
               SUM(CASE WHEN speed_kph > 0 THEN 1 ELSE 0 END)::float / NULLIF(COUNT(*),0) AS util
        FROM telemetry_data
        WHERE timestamp_utc >= :s AND timestamp_utc < :e
        GROUP BY vehicle_id
        """,
        {"s": s, "e": e},
      )
    ).all()
    return {"utilization": [{"vehicle_id": r[0], "utilization": float(r[1] or 0)} for r in rows]}
  finally:
    session.close()


@router.get("/trends", summary="Trend analysis")
def trends(request: Request, start: Optional[datetime] = Query(None), end: Optional[datetime] = Query(None), group: str = Query("day", pattern="^(hour|day|week)$")):
  _ensure_auth(request)
  s, e = _parse_dates(start, end)
  session = get_session()
  try:
    trunc = "hour" if group == "hour" else ("week" if group == "week" else "day")
    rows = (
      session.execute(
        f"""
        SELECT date_trunc('{trunc}', timestamp_utc) AS bucket,
               AVG(speed_kph), MAX(speed_kph), AVG(engine_temp_c)
        FROM telemetry_data
        WHERE timestamp_utc >= :s AND timestamp_utc < :e
        GROUP BY bucket
        ORDER BY bucket
        """,
        {"s": s, "e": e},
      )
    ).all()
    return {"items": [{"bucket": r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0]), "avg_speed_kph": float(r[1] or 0), "max_speed_kph": float(r[2] or 0), "avg_engine_temp_c": float(r[3] or 0)} for r in rows]}
  finally:
    session.close()

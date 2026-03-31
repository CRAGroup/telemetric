"""Fuel efficiency and anomaly analysis.

Provides `FuelAnalyzer` to:
- Track fuel consumption patterns
- Detect refueling events
- Identify potential fuel theft (sudden drops)
- Calculate fuel efficiency by route
- Compare against vehicle benchmarks
- Forecast fuel costs
- Recommend fuel-saving strategies
- Generate fuel analysis reports
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database.connection import get_session
from ...models.telemetry import Telemetry
from ...models.trip import Trip
from ...models.vehicle import Vehicle


@dataclass
class FuelBenchmark:
    vehicle_make: str
    vehicle_model: str
    km_per_l: float  # manufacturer or fleet benchmark


@dataclass
class FuelForecastParams:
    price_per_liter: float
    horizon_days: int = 30


class FuelAnalyzer:
    def __init__(self, benchmarks: Optional[List[FuelBenchmark]] = None) -> None:
        self.benchmarks = benchmarks or []

    def analyze(self, vehicle_id: int, *, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict[str, Any]:
        session = get_session()
        try:
            end = end or datetime.utcnow()
            start = start or (end - timedelta(days=30))

            consumption = self._consumption_patterns(session, vehicle_id, start, end)
            events = self._detect_events(session, vehicle_id, start, end)
            efficiency = self._efficiency_by_trip(session, vehicle_id, start, end)
            bench = self._benchmark_compare(session, vehicle_id, efficiency)

            return {
                "window": {"start": start.isoformat(), "end": end.isoformat()},
                "consumption": consumption,
                "events": events,
                "efficiency_by_trip": efficiency,
                "benchmarks": bench,
            }
        finally:
            session.close()

    def forecast_costs(self, vehicle_id: int, params: FuelForecastParams) -> Dict[str, Any]:
        session = get_session()
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=30)
            # approximate liters per day from telemetry fuel_level changes
            daily = (
                session.query(
                    func.date_trunc("day", Telemetry.timestamp_utc).label("day"),
                    func.avg(Telemetry.fuel_level_pct).label("avg_level"),
                )
                .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
                .group_by("day")
                .order_by("day")
            ).all()
            avg_day_change = 0.0
            if len(daily) >= 2:
                changes = []
                for i in range(1, len(daily)):
                    prev = float(daily[i - 1].avg_level or 0)
                    cur = float(daily[i].avg_level or 0)
                    changes.append(prev - cur)
                avg_day_change = sum(changes) / len(changes)
            # assume tank size from vehicle if available else 60L
            tank_size = self._vehicle_tank_size(session, vehicle_id) or 60.0
            liters_per_day = max(0.0, (avg_day_change / 100.0) * tank_size)
            total_liters = liters_per_day * params.horizon_days
            return {
                "horizon_days": params.horizon_days,
                "liters_estimate": total_liters,
                "cost_estimate": total_liters * params.price_per_liter,
            }
        finally:
            session.close()

    def recommendations(self, vehicle_id: int) -> List[str]:
        # Simple static recs; could be based on analyze() output
        return [
            "Maintain steady speeds and avoid rapid acceleration to save fuel.",
            "Ensure proper tire pressure and regular maintenance.",
            "Plan routes to reduce congestion and idling.",
            "Remove unnecessary load and avoid roof racks when possible.",
        ]

    def report(self, vehicle_id: int, params: Optional[FuelForecastParams] = None) -> Dict[str, Any]:
        analysis = self.analyze(vehicle_id)
        forecast = self.forecast_costs(vehicle_id, params or FuelForecastParams(price_per_liter=2.0))
        return {
            **analysis,
            "forecast": forecast,
            "recommendations": self.recommendations(vehicle_id),
        }

    # -------------------
    # Internals
    # -------------------
    def _consumption_patterns(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        q = (
            session.query(
                func.date_trunc("day", Telemetry.timestamp_utc).label("day"),
                func.avg(Telemetry.fuel_level_pct).label("avg_level"),
                func.avg(Telemetry.speed_kph).label("avg_speed"),
            )
            .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .group_by("day")
            .order_by("day")
        )
        res: List[Dict[str, Any]] = []
        for row in q.all():
            res.append({"day": row.day.isoformat(), "avg_level_pct": float(row.avg_level or 0), "avg_speed_kph": float(row.avg_speed or 0)})
        return res

    def _detect_events(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> Dict[str, List[Dict[str, Any]]]:
        # Identify refuels (positive jumps) and potential theft (sudden drops)
        q = (
            session.query(Telemetry.timestamp_utc, Telemetry.fuel_level_pct)
            .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .order_by(Telemetry.timestamp_utc)
        )
        rows = q.all()
        refuels: List[Dict[str, Any]] = []
        thefts: List[Dict[str, Any]] = []
        if len(rows) >= 2:
            for i in range(1, len(rows)):
                t_prev, f_prev = rows[i - 1]
                t_cur, f_cur = rows[i]
                if f_prev is None or f_cur is None:
                    continue
                delta = float(f_cur) - float(f_prev)
                if delta >= 10.0:  # heuristic: >= 10% jump
                    refuels.append({"time": t_cur.isoformat(), "delta_pct": delta})
                if delta <= -10.0:  # heuristic: <= -10% drop
                    thefts.append({"time": t_cur.isoformat(), "delta_pct": delta})
        return {"refuels": refuels, "potential_theft": thefts}

    def _efficiency_by_trip(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        q = (
            session.query(Trip.id, Trip.distance_km, Trip.fuel_used_l)
            .filter(Trip.vehicle_id == vehicle_id, Trip.start_time_utc >= start, Trip.start_time_utc < end)
            .order_by(Trip.start_time_utc)
        )
        res: List[Dict[str, Any]] = []
        for trip_id, dist, fuel in q.all():
            km_per_l = (float(dist) / float(fuel)) if dist and fuel and fuel > 0 else None
            res.append({"trip_id": trip_id, "distance_km": float(dist or 0), "fuel_used_l": float(fuel or 0), "km_per_l": km_per_l})
        return res

    def _benchmark_compare(self, session: Session, vehicle_id: int, efficiency_by_trip: List[Dict[str, Any]]) -> Dict[str, Any]:
        v = session.query(Vehicle).filter(Vehicle.id == vehicle_id).one_or_none()
        if not v:
            return {"benchmark_km_per_l": None, "below_benchmark_trips": []}
        bench = next((b for b in self.benchmarks if b.vehicle_make == v.make and b.vehicle_model == v.model), None)
        if not bench:
            return {"benchmark_km_per_l": None, "below_benchmark_trips": []}
        below = [t for t in efficiency_by_trip if t.get("km_per_l") is not None and t["km_per_l"] < bench.km_per_l]
        return {"benchmark_km_per_l": bench.km_per_l, "below_benchmark_trips": below}

    def _vehicle_tank_size(self, session: Session, vehicle_id: int) -> Optional[float]:
        v = session.query(Vehicle).filter(Vehicle.id == vehicle_id).one_or_none()
        return None if not v else v.fuel_tank_capacity

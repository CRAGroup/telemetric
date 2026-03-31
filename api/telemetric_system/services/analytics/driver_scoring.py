"""Driver behavior scoring algorithms.

Provides a weighted scoring system across harsh acceleration, hard braking,
speeding, sharp cornering, and idle time. Generates daily/weekly/monthly
scores, compares against fleet averages, identifies improvement areas,
produces coaching recommendations, and tracks trends over time.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database.connection import get_session
from ...models.telemetry import Telemetry


@dataclass(frozen=True)
class Weights:
    harsh_accel: float = 0.20
    hard_brake: float = 0.25
    speeding: float = 0.30
    sharp_corner: float = 0.15
    idle_time: float = 0.10


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


class DriverScoringService:
    def __init__(self, weights: Optional[Weights] = None) -> None:
        self.weights = weights or Weights()

    def _window(self, period: str) -> tuple[datetime, datetime]:
        now = datetime.utcnow()
        if period == "daily":
            start = now - timedelta(days=1)
        elif period == "weekly":
            start = now - timedelta(weeks=1)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            raise ValueError("period must be daily|weekly|monthly")
        return start, now

    def _metrics(self, session: Session, driver_id: int, start: datetime, end: datetime) -> Dict[str, Any]:
        q = (
            session.query(
                func.sum(func.case((Telemetry.harsh_accel.is_(True), 1), else_=0)),
                func.sum(func.case((Telemetry.hard_brake.is_(True), 1), else_=0)),
                func.sum(func.case((Telemetry.speed_kph > 120, 1), else_=0)),
                func.sum(func.case((Telemetry.sharp_corner.is_(True), 1), else_=0)),
                func.sum(func.case((Telemetry.speed_kph < 5, 1), else_=0)).label("idle_samples"),
                func.count(Telemetry.id).label("total_samples"),
                func.avg(Telemetry.speed_kph),
            )
            .filter(
                Telemetry.driver_id == driver_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
            )
        )
        row = q.one()
        harsh_accel = int(row[0] or 0)
        hard_brake = int(row[1] or 0)
        speeding = int(row[2] or 0)
        sharp_corner = int(row[3] or 0)
        idle_samples = int(row[4] or 0)
        total_samples = int(row[5] or 0)
        idle_pct = (idle_samples / total_samples * 100.0) if total_samples > 0 else 0.0
        avg_speed = float(row[6] or 0.0)
        return {
            "harsh_accel": harsh_accel,
            "hard_brake": hard_brake,
            "speeding": speeding,
            "sharp_corner": sharp_corner,
            "idle_pct": idle_pct,
            "avg_speed": avg_speed,
            "total_samples": total_samples,
        }

    def _fleet_metrics(self, session: Session, start: datetime, end: datetime) -> Dict[str, float]:
        q = (
            session.query(
                func.avg(func.cast(func.case((Telemetry.harsh_accel.is_(True), 1), else_=0), type_=float)),
                func.avg(func.cast(func.case((Telemetry.hard_brake.is_(True), 1), else_=0), type_=float)),
                func.avg(func.cast(func.case((Telemetry.speed_kph > 120, 1), else_=0), type_=float)),
                func.avg(func.cast(func.case((Telemetry.sharp_corner.is_(True), 1), else_=0), type_=float)),
                func.avg(func.cast(func.case((Telemetry.speed_kph < 5, 1), else_=0), type_=float)),
            )
            .filter(Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
        )
        row = q.one()
        return {
            "harsh_accel_rate": float(row[0] or 0.0),
            "hard_brake_rate": float(row[1] or 0.0),
            "speeding_rate": float(row[2] or 0.0),
            "sharp_corner_rate": float(row[3] or 0.0),
            "idle_rate": float(row[4] or 0.0),
        }

    def _score_from_metrics(self, m: Dict[str, Any]) -> float:
        # Normalize incident counts by samples (higher incidents => lower score)
        total = max(1, m.get("total_samples", 1))
        harsh_rate = (m.get("harsh_accel", 0) / total) * 100.0
        brake_rate = (m.get("hard_brake", 0) / total) * 100.0
        speed_rate = (m.get("speeding", 0) / total) * 100.0
        corner_rate = (m.get("sharp_corner", 0) / total) * 100.0
        idle_pct = float(m.get("idle_pct", 0.0))

        # Convert rates to sub-scores (100 - rate scaled)
        s_harsh = _clamp(100.0 - harsh_rate)
        s_brake = _clamp(100.0 - brake_rate)
        s_speed = _clamp(100.0 - speed_rate)
        s_corner = _clamp(100.0 - corner_rate)
        s_idle = _clamp(100.0 - idle_pct)

        score = (
            s_harsh * self.weights.harsh_accel
            + s_brake * self.weights.hard_brake
            + s_speed * self.weights.speeding
            + s_corner * self.weights.sharp_corner
            + s_idle * self.weights.idle_time
        )
        return _clamp(score)

    def compute_scores(self, driver_id: int) -> Dict[str, Any]:
        session = get_session()
        try:
            out: Dict[str, Any] = {"driver_id": driver_id, "periods": {}, "trends": []}
            for period in ("daily", "weekly", "monthly"):
                start, end = self._window(period)
                m = self._metrics(session, driver_id, start, end)
                fleet = self._fleet_metrics(session, start, end)
                score = self._score_from_metrics(m)
                improvement = self._improvement_areas(m, fleet)
                recs = self._recommendations(improvement)
                out["periods"][period] = {
                    "score": score,
                    "metrics": m,
                    "fleet": fleet,
                    "improvement": improvement,
                    "recommendations": recs,
                }

            # trends: weekly scores for past 8 weeks
            for i in range(8, 0, -1):
                start = datetime.utcnow() - timedelta(weeks=i)
                end = start + timedelta(weeks=1)
                m = self._metrics(session, driver_id, start, end)
                out["trends"].append({"week_start": start.date().isoformat(), "score": self._score_from_metrics(m)})

            return out
        finally:
            session.close()

    def _improvement_areas(self, m: Dict[str, Any], fleet: Dict[str, float]) -> List[str]:
        areas: List[str] = []
        total = max(1, m.get("total_samples", 1))
        if total == 0:
            return areas
        # Compare driver's rates to fleet average rates
        def rate(cnt_key: str) -> float:
            return (m.get(cnt_key, 0) / total)
        if rate("harsh_accel") > fleet.get("harsh_accel_rate", 0):
            areas.append("harsh_acceleration")
        if rate("hard_brake") > fleet.get("hard_brake_rate", 0):
            areas.append("hard_braking")
        if rate("speeding") > fleet.get("speeding_rate", 0):
            areas.append("speeding")
        if rate("sharp_corner") > fleet.get("sharp_corner_rate", 0):
            areas.append("sharp_cornering")
        # idle compare using percentage directly
        if m.get("idle_pct", 0.0) / 100.0 > fleet.get("idle_rate", 0.0):
            areas.append("idling")
        return areas

    def _recommendations(self, areas: List[str]) -> List[str]:
        recs: List[str] = []
        for a in areas:
            if a == "harsh_acceleration":
                recs.append("Accelerate smoothly to reduce wear and fuel use.")
            elif a == "hard_braking":
                recs.append("Increase following distance to avoid hard braking.")
            elif a == "speeding":
                recs.append("Observe speed limits to improve safety and score.")
            elif a == "sharp_cornering":
                recs.append("Take corners more gently to enhance stability.")
            elif a == "idling":
                recs.append("Reduce idle time by shutting off engine during long stops.")
        if not recs:
            recs.append("Great driving! Keep maintaining safe habits.")
        return recs

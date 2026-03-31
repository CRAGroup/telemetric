"""Batch processing for historical analytics.

`BatchProcessor` aggregates telemetry data (hourly/daily/weekly), computes trip
summaries, driver behavior scores, and fuel efficiency metrics, and stores
aggregated outputs for dashboards or reports.
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
from ...models.driver import Driver
from ...models.vehicle import Vehicle


@dataclass
class BatchConfig:
    lookback_days: int = 7


class BatchProcessor:
    def __init__(self, config: Optional[BatchConfig] = None) -> None:
        self.config = config or BatchConfig()

    def run(self) -> Dict[str, Any]:
        """Run all aggregations over the configured lookback period."""
        session = get_session()
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=self.config.lookback_days)

            hourly = self._aggregate(session, start, end, bucket="hour")
            daily = self._aggregate(session, start, end, bucket="day")
            weekly = self._aggregate(session, start, end, bucket="week")

            trips = self._trip_summaries(session, start, end)
            behavior = self._driver_scores(session, start, end)
            fuel = self._fuel_metrics(session, start, end)

            result = {
                "generated_at": end.isoformat(),
                "window": {"start": start.isoformat(), "end": end.isoformat()},
                "hourly": hourly,
                "daily": daily,
                "weekly": weekly,
                "trips": trips,
                "driver_scores": behavior,
                "fuel_metrics": fuel,
            }
            return result
        finally:
            session.close()

    def _aggregate(self, session: Session, start: datetime, end: datetime, *, bucket: str) -> List[Dict[str, Any]]:
        if bucket == "hour":
            trunc = func.date_trunc("hour", Telemetry.timestamp_utc)
        elif bucket == "day":
            trunc = func.date_trunc("day", Telemetry.timestamp_utc)
        elif bucket == "week":
            trunc = func.date_trunc("week", Telemetry.timestamp_utc)
        else:
            raise ValueError("Unsupported bucket")

        q = (
            session.query(
                trunc.label("bucket"),
                Telemetry.vehicle_id,
                func.avg(Telemetry.speed_kph).label("avg_speed_kph"),
                func.max(Telemetry.speed_kph).label("max_speed_kph"),
                func.avg(Telemetry.engine_temp_c).label("avg_engine_temp_c"),
            )
            .filter(Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .group_by("bucket", Telemetry.vehicle_id)
            .order_by("bucket", Telemetry.vehicle_id)
        )

        results: List[Dict[str, Any]] = []
        for row in q.all():
            results.append(
                {
                    "bucket": row.bucket.isoformat() if hasattr(row.bucket, "isoformat") else str(row.bucket),
                    "vehicle_id": row.vehicle_id,
                    "avg_speed_kph": float(row.avg_speed_kph or 0),
                    "max_speed_kph": float(row.max_speed_kph or 0),
                    "avg_engine_temp_c": float(row.avg_engine_temp_c or 0),
                }
            )
        return results

    def _trip_summaries(self, session: Session, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        q = (
            session.query(
                Trip.vehicle_id,
                func.count(Trip.id),
                func.sum(Trip.distance_km),
                func.sum(Trip.fuel_used_l),
            )
            .filter(Trip.start_time_utc >= start, Trip.start_time_utc < end)
            .group_by(Trip.vehicle_id)
        )
        res: List[Dict[str, Any]] = []
        for vid, count, dist, fuel in q.all():
            res.append(
                {
                    "vehicle_id": vid,
                    "num_trips": int(count or 0),
                    "distance_km": float(dist or 0),
                    "fuel_used_l": float(fuel or 0),
                    "avg_fuel_eff_km_per_l": (float(dist) / float(fuel)) if fuel and fuel > 0 else None,
                }
            )
        return res

    def _driver_scores(self, session: Session, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # Simple scoring: fewer speeding events => higher score
        speeding_q = (
            session.query(Telemetry.driver_id, func.count(Telemetry.id))
            .filter(
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.speed_kph.isnot(None),
                Telemetry.speed_kph > 120.0,
            )
            .group_by(Telemetry.driver_id)
        )
        speeding_map = {row[0]: int(row[1]) for row in speeding_q.all()}

        res: List[Dict[str, Any]] = []
        for driver in session.query(Driver).all():
            infractions = speeding_map.get(driver.id, 0)
            score = max(0, 100 - infractions * 5)
            res.append({"driver_id": driver.id, "score": score, "infractions": infractions})
        return res

    def _fuel_metrics(self, session: Session, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        q = (
            session.query(
                Telemetry.vehicle_id,
                func.avg(Telemetry.fuel_level_pct),
                func.avg(Telemetry.speed_kph),
            )
            .filter(Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .group_by(Telemetry.vehicle_id)
        )
        res: List[Dict[str, Any]] = []
        for vid, avg_fuel_level, avg_speed in q.all():
            res.append(
                {
                    "vehicle_id": vid,
                    "avg_fuel_level_pct": float(avg_fuel_level or 0),
                    "avg_speed_kph": float(avg_speed or 0),
                }
            )
        return res

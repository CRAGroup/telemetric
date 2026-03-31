"""Pattern recognition and anomaly detection.

Detects recurring routes, unusual behavior, peak usage times, inefficient routes,
after-hours usage, and maintenance patterns. Uses clustering and anomaly
methods when available; falls back to heuristics otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database.connection import get_session
from ...models.telemetry import Telemetry
from ...models.trip import Trip
from ...models.maintenance import MaintenanceRecord

try:
    from sklearn.cluster import KMeans, DBSCAN  # type: ignore
    from sklearn.ensemble import IsolationForest  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    KMeans = None  # type: ignore
    DBSCAN = None  # type: ignore
    IsolationForest = None  # type: ignore
    np = None  # type: ignore


@dataclass
class PatternParams:
    lookback_days: int = 30
    work_hours_start: time = time(7, 0)
    work_hours_end: time = time(19, 0)


class PatternDetectionService:
    def __init__(self, params: Optional[PatternParams] = None) -> None:
        self.params = params or PatternParams()

    def analyze(self, vehicle_id: int) -> Dict[str, Any]:
        session = get_session()
        try:
            end = datetime.utcnow()
            start = end - timedelta(days=self.params.lookback_days)

            routes = self._recurring_routes(session, vehicle_id, start, end)
            unusual = self._unusual_behavior(session, vehicle_id, start, end)
            peaks = self._peak_usage(session, vehicle_id, start, end)
            inefficient = self._inefficient_routes(session, vehicle_id, start, end)
            after_hours = self._after_hours_usage(session, vehicle_id, start, end)
            maintenance = self._maintenance_patterns(session, vehicle_id)

            return {
                "routes": routes,
                "unusual": unusual,
                "peaks": peaks,
                "inefficient": inefficient,
                "after_hours": after_hours,
                "maintenance": maintenance,
            }
        finally:
            session.close()

    def _recurring_routes(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # Use trip endpoints as route features; cluster start/end pairs
        q = (
            session.query(
                Trip.id,
                Trip.start_lat,
                Trip.start_lng,
                Trip.end_lat,
                Trip.end_lng,
                Trip.distance_km,
            )
            .filter(Trip.vehicle_id == vehicle_id, Trip.start_time_utc >= start, Trip.start_time_utc < end)
        )
        rows = q.all()
        if not rows:
            return []
        features = []
        for r in rows:
            if None in (r.start_lat, r.start_lng, r.end_lat, r.end_lng):
                continue
            features.append([float(r.start_lat), float(r.start_lng), float(r.end_lat), float(r.end_lng)])
        if not features:
            return []
        if KMeans and np is not None:
            k = min(5, max(1, len(features) // 5))
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(np.array(features))
            clusters: Dict[int, List[int]] = {}
            for idx, label in enumerate(labels):
                clusters.setdefault(int(label), []).append(rows[idx].id)
            return [{"cluster": c, "trip_ids": ids, "count": len(ids)} for c, ids in clusters.items()]
        # heuristic fallback: group by rounded coordinates
        buckets: Dict[str, List[int]] = {}
        for r in rows:
            key = f"{round(r.start_lat or 0, 2)}:{round(r.start_lng or 0, 2)}->{round(r.end_lat or 0, 2)}:{round(r.end_lng or 0, 2)}"
            buckets.setdefault(key, []).append(r.id)
        return [{"route": k, "trip_ids": v, "count": len(v)} for k, v in buckets.items() if len(v) > 1]

    def _unusual_behavior(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # Use speed and engine temp as anomaly features
        q = (
            session.query(Telemetry.id, Telemetry.speed_kph, Telemetry.engine_temp_c)
            .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
        )
        rows = q.all()
        if not rows:
            return []
        X = []
        ids = []
        for i, s, t in rows:
            X.append([float(s or 0), float(t or 0)])
            ids.append(int(i))
        if IsolationForest and np is not None and len(X) >= 20:
            model = IsolationForest(contamination=0.05, random_state=42)
            preds = model.fit_predict(np.array(X))
            outliers = [ids[i] for i, p in enumerate(preds) if p == -1]
            return [{"telemetry_id": tid} for tid in outliers]
        # heuristic: mark points beyond z-score > 3
        import statistics

        speeds = [x[0] for x in X]
        temps = [x[1] for x in X]
        mean_s, stdev_s = statistics.fmean(speeds), (statistics.pstdev(speeds) or 1.0)
        mean_t, stdev_t = statistics.fmean(temps), (statistics.pstdev(temps) or 1.0)
        res = []
        for idx, (s, t) in enumerate(X):
            if abs((s - mean_s) / stdev_s) > 3 or abs((t - mean_t) / stdev_t) > 3:
                res.append({"telemetry_id": ids[idx]})
        return res

    def _peak_usage(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> Dict[str, Any]:
        hours = (
            session.query(func.extract("hour", Telemetry.timestamp_utc), func.count(Telemetry.id))
            .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .group_by(func.extract("hour", Telemetry.timestamp_utc))
            .order_by(func.extract("hour", Telemetry.timestamp_utc))
        ).all()
        return {int(h): int(c) for h, c in hours}

    def _inefficient_routes(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # Inefficiency heuristic: low avg speed or high idle samples per trip
        q = (
            session.query(Trip.id, func.avg(Telemetry.speed_kph), func.sum(func.case((Telemetry.speed_kph < 5, 1), else_=0)))
            .join(Telemetry, Telemetry.vehicle_id == Trip.vehicle_id)
            .filter(
                Trip.vehicle_id == vehicle_id,
                Trip.start_time_utc >= start,
                Trip.start_time_utc < end,
                Telemetry.timestamp_utc >= Trip.start_time_utc,
                Telemetry.timestamp_utc <= func.coalesce(Trip.end_time_utc, Telemetry.timestamp_utc),
            )
            .group_by(Trip.id)
        )
        res: List[Dict[str, Any]] = []
        for trip_id, avg_speed, idle_samples in q.all():
            if (avg_speed or 0) < 20.0 or (idle_samples or 0) > 60:  # thresholds
                res.append({"trip_id": int(trip_id), "avg_speed_kph": float(avg_speed or 0), "idle_samples": int(idle_samples or 0)})
        return res

    def _after_hours_usage(self, session: Session, vehicle_id: int, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        rows = (
            session.query(Telemetry.id, Telemetry.timestamp_utc)
            .filter(Telemetry.vehicle_id == vehicle_id, Telemetry.timestamp_utc >= start, Telemetry.timestamp_utc < end)
            .all()
        )
        res: List[Dict[str, Any]] = []
        s, e = self.params.work_hours_start, self.params.work_hours_end
        for tid, ts in rows:
            if ts is None:
                continue
            hr = ts.time()
            if not (s <= hr <= e):
                res.append({"telemetry_id": int(tid), "time": ts.isoformat()})
        return res

    def _maintenance_patterns(self, session: Session, vehicle_id: int) -> Dict[str, Any]:
        rows = (
            session.query(MaintenanceRecord.service_type, func.count(MaintenanceRecord.id), func.avg(MaintenanceRecord.cost))
            .filter(MaintenanceRecord.vehicle_id == vehicle_id)
            .group_by(MaintenanceRecord.service_type)
            .all()
        )
        return {str(t or "unknown"): {"count": int(c or 0), "avg_cost": float(avg or 0)} for t, c, avg in rows}

"""Alert processing engine for real-time conditions.

Processes:
- Real-time alerts (immediate violations)
- Threshold-based alerts
- Scheduled alerts (maintenance due)
- Anomaly-based alerts
- Alert priority levels (critical, high, medium, low)
- Alert deduplication and aggregation
- Alert lifecycle: created, acknowledged, resolved
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_

from ...core.database.connection import get_session
from ...models.alert import Alert


@dataclass
class AlertRule:
    type: str
    threshold: Optional[float] = None
    window_s: int = 300
    priority: str = "medium"  # critical|high|medium|low
    dedup_s: int = 300


class AlertEngine:
    def __init__(self, rules: Optional[List[AlertRule]] = None) -> None:
        self.rules = rules or []

    # ---------------------
    # Real-time processing
    # ---------------------
    def process_realtime(self, vehicle_id: int, payload: Dict[str, Any]) -> List[int]:
        created: List[int] = []
        speed = payload.get("vehicle", {}).get("speed_kph") or payload.get("vehicle", {}).get("speed_kph_smoothed")
        if speed and self._should_fire("speed_limit", value=float(speed)):
            alert_id = self._create_alert(vehicle_id, "speed_limit", f"Speed {speed} kph exceeded limit", priority="high")
            if alert_id:
                created.append(alert_id)
        # Add more immediate checks as needed
        return created

    # ---------------------
    # Threshold-based
    # ---------------------
    def process_thresholds(self, vehicle_id: int, metrics: Dict[str, float]) -> List[int]:
        created: List[int] = []
        for rule in self.rules:
            if rule.threshold is None:
                continue
            value = metrics.get(rule.type)
            if value is None:
                continue
            if value >= rule.threshold and self._respect_dedup(vehicle_id, rule.type, rule.dedup_s):
                alert_id = self._create_alert(vehicle_id, rule.type, f"{rule.type}={value} exceeded {rule.threshold}", priority=rule.priority)
                if alert_id:
                    created.append(alert_id)
        return created

    # ---------------------
    # Scheduled alerts
    # ---------------------
    def process_scheduled(self, vehicle_id: int, due_in_km: float, due_date: str) -> Optional[int]:
        msg = f"Maintenance due in {int(due_in_km)} km or by {due_date}"
        return self._create_alert(vehicle_id, "maintenance_due", msg, priority="medium")

    # ---------------------
    # Anomaly-based
    # ---------------------
    def process_anomaly(self, vehicle_id: int, anomalies: List[Dict[str, Any]]) -> Optional[int]:
        if not anomalies:
            return None
        msg = f"Detected {len(anomalies)} anomalous readings"
        return self._create_alert(vehicle_id, "anomaly_detected", msg, priority="medium")

    # ---------------------
    # Lifecycle
    # ---------------------
    def acknowledge(self, alert_id: int) -> bool:
        session = get_session()
        try:
            a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
            if not a:
                return False
            a.acknowledged = True
            a.acknowledged_at = datetime.now(tz=timezone.utc)
            session.add(a)
            session.commit()
            return True
        finally:
            session.close()

    def resolve(self, alert_id: int) -> bool:
        session = get_session()
        try:
            a = session.query(Alert).filter(Alert.id == alert_id, Alert.is_deleted.is_(False)).one_or_none()
            if not a:
                return False
            a.is_deleted = True  # soft-resolve
            session.add(a)
            session.commit()
            return True
        finally:
            session.close()

    # ---------------------
    # Internals
    # ---------------------
    def _should_fire(self, rule_type: str, *, value: float) -> bool:
        for r in self.rules:
            if r.type == rule_type and r.threshold is not None:
                return value >= r.threshold and self._respect_dedup(None, rule_type, r.dedup_s)
        return False

    def _respect_dedup(self, vehicle_id: Optional[int], alert_type: str, dedup_s: int) -> bool:
        session = get_session()
        try:
            since = datetime.utcnow() - timedelta(seconds=dedup_s)
            q = session.query(Alert).filter(Alert.alert_type == alert_type, Alert.created_at >= since)
            if vehicle_id is not None:
                q = q.filter(Alert.vehicle_id == vehicle_id)
            exists = session.query(q.exists()).scalar()
            return not bool(exists)
        finally:
            session.close()

    def _create_alert(self, vehicle_id: int, alert_type: str, message: str, *, priority: str) -> Optional[int]:
        # Aggregation: if a similar alert exists recently, append count in message
        session = get_session()
        try:
            since = datetime.utcnow() - timedelta(minutes=10)
            existing = (
                session.query(Alert)
                .filter(
                    Alert.vehicle_id == vehicle_id,
                    Alert.alert_type == alert_type,
                    Alert.created_at >= since,
                    Alert.is_deleted.is_(False),
                )
                .order_by(Alert.created_at.desc())
                .first()
            )
            if existing:
                existing.message = f"{existing.message} | another occurrence at {datetime.utcnow().isoformat()}"
                session.add(existing)
                session.commit()
                return existing.id

            a = Alert(
                vehicle_id=vehicle_id,
                driver_id=None,
                alert_type=alert_type,
                message=message,
                severity=priority,
                acknowledged=False,
            )
            session.add(a)
            session.commit()
            return a.id  # type: ignore[attr-defined]
        finally:
            session.close()

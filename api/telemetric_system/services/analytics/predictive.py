"""Predictive analytics and forecasting.

Predictive maintenance service that:
- Analyzes engine parameters for wear patterns
- Predicts maintenance needs based on odometer, engine hours, DTC frequency,
  oil condition indicators, and battery health
- Calculates optimal maintenance schedule and estimated costs
- Prioritizes maintenance urgency and sends proactive alerts

Uses a simple ML model if scikit-learn is available, with rule-based fallback.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.database.connection import get_session
from ...models.alert import Alert, AlertSeverity
from ...models.maintenance import MaintenanceRecord
from ...models.telemetry import Telemetry
from ...models.vehicle import Vehicle

try:
    # Optional ML support
    from sklearn.tree import DecisionTreeRegressor  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    DecisionTreeRegressor = None  # type: ignore
    np = None  # type: ignore


@dataclass
class PredictiveParams:
    lookback_days: int = 90
    target_service_km: float = 10000.0  # typical service interval
    base_cost: float = 100.0  # base service cost
    per_km_cost: float = 0.02  # variable cost estimate
    dtc_weight: float = 0.25
    oil_weight: float = 0.30
    battery_weight: float = 0.20
    hours_weight: float = 0.25


class PredictiveMaintenanceService:
    def __init__(self, params: Optional[PredictiveParams] = None) -> None:
        self.params = params or PredictiveParams()
        self._model = None  # type: ignore

    # -------------------
    # Public API
    # -------------------
    def analyze_vehicle(self, vehicle_id: int) -> Dict[str, Any]:
        session = get_session()
        try:
            features = self._collect_features(session, vehicle_id)
            prediction = self._predict(features)
            schedule = self._schedule(features, prediction)
            cost = self._estimate_cost(features, prediction)
            urgency = self._urgency(features, prediction)
            return {
                "vehicle_id": vehicle_id,
                "features": features,
                "prediction": prediction,
                "schedule": schedule,
                "cost_estimate": cost,
                "urgency": urgency,
            }
        finally:
            session.close()

    def send_proactive_alerts(self, vehicle_id: int) -> Optional[int]:
        """Create an alert if urgency is high. Returns alert ID or None."""
        result = self.analyze_vehicle(vehicle_id)
        if result["urgency"]["level"] != "high":
            return None
        session = get_session()
        try:
            a = Alert(
                vehicle_id=vehicle_id,
                driver_id=None,
                alert_type="predictive_maintenance",
                message=f"Maintenance due in {int(result['schedule']['due_in_km'])} km or by {result['schedule']['due_date']}",
                severity=AlertSeverity.WARNING.value,
            )
            session.add(a)
            session.commit()
            return a.id  # type: ignore[attr-defined]
        finally:
            session.close()

    # -------------------
    # Internals
    # -------------------
    def _collect_features(self, session: Session, vehicle_id: int) -> Dict[str, Any]:
        end = datetime.utcnow()
        start = end - timedelta(days=self.params.lookback_days)

        v: Optional[Vehicle] = session.query(Vehicle).filter(Vehicle.id == vehicle_id).one_or_none()
        odometer = float(v.current_odometer) if v and v.current_odometer is not None else 0.0

        # Engine hours proxy: number of telemetry samples with rpm > 0 times 1 minute
        rpm_samples = (
            session.query(func.count(Telemetry.id))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.rpm.isnot(None),
                Telemetry.rpm > 0,
            )
            .scalar()
            or 0
        )
        engine_hours = rpm_samples / 60.0  # assume 1-min sampling cadence if present

        # DTC frequency proxy: count of alerts of type diagnostics or number of Telemetry with flags (not modeled), so use rpm>0 & engine_temp high
        dtc_like = (
            session.query(func.count(Telemetry.id))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.engine_temp_c.isnot(None),
                Telemetry.engine_temp_c > 105.0,
            )
            .scalar()
            or 0
        )

        # Oil condition indicators proxy: average engine_temp_c and engine_load_pct
        oil_temp_avg = (
            session.query(func.avg(Telemetry.engine_temp_c))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.engine_temp_c.isnot(None),
            )
            .scalar()
        )
        engine_load_avg = (
            session.query(func.avg(Telemetry.engine_load_pct))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.engine_load_pct.isnot(None),
            )
            .scalar()
        )

        # Battery health proxy: fraction of samples below 12.0V
        low_batt_samples = (
            session.query(func.count(Telemetry.id))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.battery_voltage_v.isnot(None),
                Telemetry.battery_voltage_v < 12.0,
            )
            .scalar()
            or 0
        )
        total_batt_samples = (
            session.query(func.count(Telemetry.id))
            .filter(
                Telemetry.vehicle_id == vehicle_id,
                Telemetry.timestamp_utc >= start,
                Telemetry.timestamp_utc < end,
                Telemetry.battery_voltage_v.isnot(None),
            )
            .scalar()
            or 1
        )
        low_batt_rate = low_batt_samples / max(1, total_batt_samples)

        # Recent maintenance distance since last record
        last_maint: Optional[MaintenanceRecord] = (
            session.query(MaintenanceRecord)
            .filter(MaintenanceRecord.vehicle_id == vehicle_id)
            .order_by(MaintenanceRecord.service_date.desc())
            .first()
        )
        km_since_maintenance = odometer  # best effort
        if last_maint is not None and last_maint.odometer_km is not None:
            try:
                km_since_maintenance = max(0.0, odometer - float(last_maint.odometer_km))
            except Exception:
                km_since_maintenance = odometer

        return {
            "odometer_km": odometer,
            "engine_hours": engine_hours,
            "dtc_frequency": dtc_like,
            "oil_temp_avg_c": float(oil_temp_avg or 0.0),
            "engine_load_avg_pct": float(engine_load_avg or 0.0),
            "low_battery_rate": float(low_batt_rate),
            "km_since_maintenance": km_since_maintenance,
        }

    def _predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Return predicted remaining_km and remaining_days before maintenance."""
        # ML path if available and model trained; otherwise heuristic
        if DecisionTreeRegressor and np is not None and self._model is not None:
            X = np.array(
                [
                    [
                        features["km_since_maintenance"],
                        features["engine_hours"],
                        features["dtc_frequency"],
                        features["oil_temp_avg_c"],
                        features["engine_load_avg_pct"],
                        features["low_battery_rate"],
                    ]
                ]
            )
            remaining_km = float(max(0.0, self._model.predict(X)[0]))
        else:
            # Heuristic: reduce remaining_km from target based on weighted stressors
            stress = 0.0
            stress += (features["dtc_frequency"] / 50.0) * self.params.dtc_weight
            stress += max(0.0, (features["oil_temp_avg_c"] - 95.0) / 20.0) * self.params.oil_weight
            stress += (features["low_battery_rate"]) * self.params.battery_weight
            stress += (features["engine_hours"] / 500.0) * self.params.hours_weight
            stress = min(1.5, stress)
            remaining_km = max(0.0, self.params.target_service_km * (1.0 - stress))
        # Convert to days based on simple average 60 km/day
        remaining_days = remaining_km / 60.0
        return {"remaining_km": remaining_km, "remaining_days": remaining_days}

    def _schedule(self, features: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
        due_in_km = prediction["remaining_km"]
        due_in_days = prediction["remaining_days"]
        due_date = (datetime.utcnow() + timedelta(days=due_in_days)).date().isoformat()
        return {"due_in_km": due_in_km, "due_in_days": due_in_days, "due_date": due_date}

    def _estimate_cost(self, features: Dict[str, Any], prediction: Dict[str, Any]) -> float:
        # Cost grows with stress and proximity to due
        stress_k = 1.0 - min(1.0, prediction["remaining_km"] / max(1.0, self.params.target_service_km))
        return self.params.base_cost + self.params.per_km_cost * features["km_since_maintenance"] * (1.0 + stress_k)

    def _urgency(self, features: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
        km = prediction["remaining_km"]
        days = prediction["remaining_days"]
        if km < 500 or days < 7:
            level = "high"
        elif km < 2000 or days < 21:
            level = "medium"
        else:
            level = "low"
        return {"level": level, "remaining_km": km, "remaining_days": days}

    # Optional: simple training stub (would require labeled historical data)
    def train(self, X: List[List[float]], y: List[float]) -> None:
        if DecisionTreeRegressor is None or np is None:
            return
        model = DecisionTreeRegressor(max_depth=5, random_state=42)
        model.fit(np.array(X), np.array(y))
        self._model = model

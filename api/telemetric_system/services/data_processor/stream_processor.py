"""Real-time stream processing pipeline.

Async `StreamProcessor` that receives telemetry in real time, enriches with
vehicle/driver info, computes derived metrics, detects violations, triggers
alerts, publishes to WebSocket, and stores results to the database.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ...core.database.connection import get_session
from ...models.alert import Alert, AlertSeverity
from ...models.telemetry import Telemetry
from ...models.vehicle import Vehicle
from ...models.driver import Driver

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    speed_limit_kph: float = 120.0
    harsh_brake_threshold_g: float = 0.4  # if provided as g-force in input


class StreamProcessor:
    def __init__(self, config: Optional[StreamConfig] = None) -> None:
        self.config = config or StreamConfig()
        self._queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=5000)
        self._ws_publish: Optional[callable] = None  # set via set_websocket_publisher

    def set_websocket_publisher(self, publisher: callable) -> None:
        """Register a coroutine function: async def publish(event: str, payload: dict) -> None"""
        self._ws_publish = publisher

    async def enqueue(self, payload: Dict[str, Any]) -> None:
        await self._queue.put(payload)

    async def run(self) -> None:
        while True:
            payload = await self._queue.get()
            try:
                await self._process(payload)
            except Exception as exc:
                logger.exception("stream process error: %s", exc)
            finally:
                self._queue.task_done()

    async def _process(self, payload: Dict[str, Any]) -> None:
        # Enrich
        enriched = await asyncio.to_thread(self._enrich, payload)
        # Metrics
        metrics = self._derive_metrics(enriched)
        # Violations & alerts
        alerts = await asyncio.to_thread(self._detect_and_persist_alerts, enriched, metrics)
        # Store telemetry
        await asyncio.to_thread(self._persist_telemetry, enriched)
        # Publish to WebSocket
        await self._publish_ws({"type": "telemetry", "data": enriched, "metrics": metrics, "alerts": alerts})

    def _enrich(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        session = get_session()
        try:
            vehicle_identifier = payload.get("vehicle_id") or payload.get("vehicle", {}).get("vehicle_id")
            if not vehicle_identifier:
                return payload
            vehicle = (
                session.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_identifier, Vehicle.is_deleted.is_(False)).one_or_none()
            )
            if vehicle is None:
                return payload
            driver = session.query(Driver).filter(Driver.id == vehicle.driver_id, Driver.is_deleted.is_(False)).one_or_none()
            payload["vehicle_db_id"] = vehicle.id
            payload["vehicle_info"] = {"id": vehicle.id, "make": vehicle.make, "model": vehicle.model, "status": vehicle.status.value if hasattr(vehicle.status, "value") else str(vehicle.status)}
            if driver:
                payload["driver_info"] = {"id": driver.id, "name": f"{driver.first_name} {driver.last_name}"}
            return payload
        finally:
            session.close()

    def _derive_metrics(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        engine = payload.get("engine", {})
        vehicle = payload.get("vehicle", {})
        speed = vehicle.get("speed_kph") or vehicle.get("speed_kph_smoothed")
        fuel_rate_lph = engine.get("fuel_rate_lph")  # liters/hour if present
        fuel_eff_km_per_l = None
        if fuel_rate_lph and speed and fuel_rate_lph > 0:
            # km/h divided by l/h = km per liter
            try:
                fuel_eff_km_per_l = float(speed) / float(fuel_rate_lph)
            except Exception:
                fuel_eff_km_per_l = None
        avg_speed = speed  # simple placeholder; could be windowed average
        return {
            "fuel_eff_km_per_l": fuel_eff_km_per_l,
            "avg_speed_kph": avg_speed,
        }

    def _detect_and_persist_alerts(self, payload: Dict[str, Any], metrics: Dict[str, Any]) -> list[Dict[str, Any]]:
        alerts: list[Dict[str, Any]] = []
        vehicle_db_id = payload.get("vehicle_db_id")
        if not vehicle_db_id:
            return alerts
        vehicle = payload.get("vehicle", {})
        engine = payload.get("engine", {})
        speed = vehicle.get("speed_kph") or vehicle.get("speed_kph_smoothed")
        hard_brake_g = engine.get("hard_brake_g")  # if provided by device

        session = get_session()
        try:
            if speed and float(speed) > self.config.speed_limit_kph:
                a = Alert(
                    vehicle_id=vehicle_db_id,
                    driver_id=None,
                    alert_type="speed_limit",
                    message=f"Speed {speed} kph exceeds limit {self.config.speed_limit_kph}",
                    severity=AlertSeverity.WARNING.value,
                )
                session.add(a)
                alerts.append({"type": "speed_limit", "severity": "warning"})

            if hard_brake_g and float(hard_brake_g) > self.config.harsh_brake_threshold_g:
                a = Alert(
                    vehicle_id=vehicle_db_id,
                    driver_id=None,
                    alert_type="harsh_brake",
                    message=f"Harsh braking {hard_brake_g}g exceeds threshold {self.config.harsh_brake_threshold_g}",
                    severity=AlertSeverity.WARNING.value,
                )
                session.add(a)
                alerts.append({"type": "harsh_brake", "severity": "warning"})

            session.commit()
        finally:
            session.close()

        return alerts

    def _persist_telemetry(self, payload: Dict[str, Any]) -> None:
        vehicle_db_id = payload.get("vehicle_db_id")
        if not vehicle_db_id:
            return
        engine = payload.get("engine", {})
        vehicle = payload.get("vehicle", {})
        ts = payload.get("timestamp")
        session = get_session()
        try:
            t = Telemetry(
                vehicle_id=vehicle_db_id,
                driver_id=None,
                timestamp_utc=None,
                rpm=_num(engine.get("rpm")),
                engine_temp_c=_num(engine.get("engine_temp_c")),
                oil_pressure_kpa=_num(engine.get("oil_pressure_kpa")),
                battery_voltage_v=_num(engine.get("battery_voltage_v")),
                throttle_pos_pct=_num(engine.get("throttle_pos_pct")),
                engine_load_pct=_num(engine.get("engine_load_pct")),
                latitude=_num(vehicle.get("lat")),
                longitude=_num(vehicle.get("lon")),
                speed_kph=_num(vehicle.get("speed_kph")) or _num(vehicle.get("speed_kph_smoothed")),
                heading_deg=_num(vehicle.get("heading_deg")),
                altitude_m=_num(vehicle.get("alt_m")),
                fuel_level_pct=_num(engine.get("fuel_level_pct")),
                fuel_rate_lph=_num(engine.get("fuel_rate_lph")),
                harsh_accel=None,
                hard_brake=None,
                sharp_corner=None,
                speeding=None,
                seatbelt_used=None,
            )
            session.add(t)
            session.commit()
        finally:
            session.close()

    async def _publish_ws(self, message: Dict[str, Any]) -> None:
        if not self._ws_publish:
            return
        try:
            await self._ws_publish("telemetry", message)
        except Exception as exc:
            logger.exception("ws publish failed: %s", exc)


def _num(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None

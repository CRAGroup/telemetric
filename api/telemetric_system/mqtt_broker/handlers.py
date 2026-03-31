"""MQTT message handlers.

Handles topics following the structure: vehicles/{vehicle_id}/{data_type}

Supported data_type values:
- telemetry: telemetry data ingestion
- alert_ack: alert acknowledgment
- config: configuration updates
- cmd_resp: command responses from device
- heartbeat: device heartbeat
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from ..core.database.connection import session_scope
from ..models.alert import Alert
from ..models.telemetry import Telemetry
from ..models.vehicle import Vehicle

logger = logging.getLogger(__name__)


def _parse_topic(topic: str) -> Optional[Tuple[str, str]]:
    """Parse MQTT topic and return (vehicle_id, data_type)."""
    try:
        parts = topic.split("/")
        if len(parts) < 3:
            return None
        if parts[0] != "vehicles":
            return None
        vehicle_id = parts[1]
        data_type = parts[2]
        return vehicle_id, data_type
    except Exception:
        return None


def _load_json(payload: bytes | str) -> Optional[Dict[str, Any]]:
    try:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8", errors="ignore")
        return json.loads(payload)
    except Exception:
        return None


def handle_message(topic: str, payload: bytes | str) -> None:
    """Dispatch handler based on topic."""
    parsed = _parse_topic(topic)
    body = _load_json(payload)
    if not parsed or body is None:
        logger.warning("MQTT invalid message topic=%s", topic)
        return

    vehicle_id, data_type = parsed
    try:
        if data_type == "telemetry":
            _handle_telemetry(vehicle_id, body)
        elif data_type == "alert_ack":
            _handle_alert_ack(vehicle_id, body)
        elif data_type == "config":
            _handle_config_update(vehicle_id, body)
        elif data_type == "cmd_resp":
            _handle_command_response(vehicle_id, body)
        elif data_type == "heartbeat":
            _handle_heartbeat(vehicle_id, body)
        else:
            logger.info("MQTT unhandled data_type=%s for vehicle=%s", data_type, vehicle_id)
    except Exception as exc:
        logger.exception("MQTT handler error for topic=%s: %s", topic, exc)


def _get_vehicle_db_id(session, vehicle_identifier: str) -> Optional[int]:
    v = session.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_identifier, Vehicle.is_deleted.is_(False)).one_or_none()
    return None if v is None else v.id


def _handle_telemetry(vehicle_identifier: str, body: Dict[str, Any]) -> None:
    """Handle telemetry - UPDATED to accept both formats"""
    with session_scope() as session:
        vehicle_db_id = _get_vehicle_db_id(session, vehicle_identifier)
        if vehicle_db_id is None:
            logger.warning("telemetry for unknown vehicle_id=%s", vehicle_identifier)
            return

        # Handle timestamp
        ts = body.get("timestamp")
        try:
            # Try both formats
            if isinstance(ts, str):
                timestamp_utc = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                timestamp_utc = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        except Exception:
            timestamp_utc = datetime.now(tz=timezone.utc)

        # Accept BOTH "vehicle" and "location" keys
        location_data = body.get("vehicle", body.get("location", {}))
        engine_data = body.get("engine", {})

        # Handle different field name variations
        t = Telemetry(
            vehicle_id=vehicle_db_id,
            driver_id=None,
            timestamp_utc=timestamp_utc.replace(tzinfo=None),

            # GPS data - handle both formats
            latitude=_num(location_data.get("lat") or location_data.get("latitude")),
            longitude=_num(location_data.get("lon") or location_data.get("longitude")),
            speed_kph=_num(location_data.get("speed_kph") or location_data.get("speed")),
            heading_deg=_num(location_data.get("heading_deg") or location_data.get("heading")),
            altitude_m=_num(location_data.get("alt_m") or location_data.get("altitude")),

            # Engine data
            rpm=_num(engine_data.get("rpm")),
            engine_temp_c=_num(engine_data.get("engine_temp_c") or engine_data.get("temperature")),
            oil_pressure_kpa=_num(engine_data.get("oil_pressure")),
            battery_voltage_v=_num(engine_data.get("battery_voltage_v") or engine_data.get("battery_voltage")),
            throttle_pos_pct=_num(engine_data.get("throttle_pos_pct") or engine_data.get("throttle_position")),
            engine_load_pct=_num(engine_data.get("engine_load_pct") or engine_data.get("load")),
            fuel_level_pct=_num(
                engine_data.get("fuel_level_pct") or engine_data.get("fuel_level") or body.get("fuel", {}).get(
                    "level")),

            fuel_rate_lph=_num(engine_data.get("fuel_rate")),
            harsh_accel=None,
            hard_brake=None,
            sharp_corner=None,
            speeding=None,
            seatbelt_used=None,
        )
        session.add(t)
        logger.info(
            f"Telemetry saved: vehicle={vehicle_identifier}, lat={t.latitude}, lon={t.longitude}, speed={t.speed_kph} oil_pressure={t.oil_pressure_kpa} battery_voltage={t.battery_voltage_v} throttle_pos={t.throttle_pos_pct} engine_load={t.engine_load_pct} fuel_level={t.fuel_level_pct} fuel_rate={t.fuel_rate_lph}")

def _handle_alert_ack(vehicle_identifier: str, body: Dict[str, Any]) -> None:
    """Mark an alert as acknowledged."""
    alert_id = body.get("alert_id")
    if not alert_id:
        logger.warning("alert_ack missing alert_id for vehicle=%s", vehicle_identifier)
        return
    with session_scope() as session:
        alert = session.query(Alert).filter(Alert.id == int(alert_id), Alert.is_deleted.is_(False)).one_or_none()
        if not alert:
            logger.warning("alert_ack unknown alert_id=%s", alert_id)
            return
        alert.acknowledged = True
        alert.acknowledged_at = datetime.now(tz=timezone.utc)
        session.add(alert)


def _handle_config_update(vehicle_identifier: str, body: Dict[str, Any]) -> None:
    """Process device/app configuration updates.

    For now, this logs the update for auditing; integration with a dynamic
    configuration store (e.g., Redis/DB) can be added here.
    """
    logger.info("config update for vehicle=%s: %s", vehicle_identifier, json.dumps(body, separators=(",", ":")))


def _handle_command_response(vehicle_identifier: str, body: Dict[str, Any]) -> None:
    """Process responses from devices to previously issued commands."""
    status = body.get("status")
    logger.info("command response vehicle=%s status=%s body=%s", vehicle_identifier, status, json.dumps(body, separators=(",", ":")))


def _handle_heartbeat(vehicle_identifier: str, body: Dict[str, Any]) -> None:
    """Handle heartbeat pings from devices."""
    ts = body.get("timestamp")
    logger.debug("heartbeat vehicle=%s ts=%s", vehicle_identifier, ts)


def _num(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None

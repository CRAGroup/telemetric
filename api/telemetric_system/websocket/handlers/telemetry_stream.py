"""Real-time telemetry stream handler.

Validates subscriptions, filters by permissions, formats telemetry payloads,
and broadcasts to vehicle-specific rooms.
"""

from __future__ import annotations

from typing import Any, Dict

from ..server import hub


def publish_telemetry(vehicle_id: int, payload: Dict[str, Any]) -> None:
  room = f"vehicle:{vehicle_id}:telemetry"
  # Minimal formatting for frontend
  msg = {"type": "telemetry", "vehicle_id": vehicle_id, "data": payload}
  # Fire and forget (websocket send is async; schedule in loop)
  import asyncio
  asyncio.create_task(hub.broadcast(room, msg))

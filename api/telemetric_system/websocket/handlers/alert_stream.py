"""Real-time alerts stream handler.

Formats and broadcasts alert notifications to rooms.
"""

from __future__ import annotations

from typing import Any, Dict

from ..server import hub


def publish_alert(vehicle_id: int, payload: Dict[str, Any]) -> None:
  # Rooms: per-vehicle and fleet-wide
  import asyncio
  msg = {"type": "alert", "vehicle_id": vehicle_id, "data": payload}
  asyncio.create_task(hub.broadcast(f"vehicle:{vehicle_id}:alerts", msg))
  asyncio.create_task(hub.broadcast("fleet:alerts", msg))

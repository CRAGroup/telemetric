"""Real-time location stream handler.

Formats and broadcasts location updates suitable for map rendering.
"""

from __future__ import annotations

from typing import Any, Dict

from ..server import hub


def publish_location(vehicle_id: int, lat: float, lon: float, heading: float | None = None, speed_kph: float | None = None) -> None:
  import asyncio
  msg: Dict[str, Any] = {"type": "location", "vehicle_id": vehicle_id, "lat": lat, "lon": lon}
  if heading is not None:
    msg["heading_deg"] = heading
  if speed_kph is not None:
    msg["speed_kph"] = speed_kph
  asyncio.create_task(hub.broadcast(f"vehicle:{vehicle_id}:location", msg))

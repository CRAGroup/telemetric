"""Boundary violation detection service.

Provides real-time geofence checks using an R-tree for spatial indexing.
- Point-in-polygon checks
- Entry/exit detection
- Dwell time tracking and violations
- Time spent in geofences and reports
Optimized for performance.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from shapely.geometry import Point
from shapely.prepared import prep

try:
  from rtree import index as rtree_index  # type: ignore
except Exception:  # pragma: no cover
  rtree_index = None  # type: ignore


@dataclass
class FenceRuntime:
  id: int
  geometry: any
  prepared: any


@dataclass
class TrackState:
  inside: Dict[int, float] = field(default_factory=dict)  # fence_id -> enter_ts
  last_point: Optional[Tuple[float, float]] = None
  last_ts: Optional[float] = None


class BoundaryChecker:
  def __init__(self, dwell_threshold_s: float = 300.0) -> None:
    self._fences: Dict[int, FenceRuntime] = {}
    self._idx = rtree_index.Index() if rtree_index else None
    self._dwell_threshold_s = dwell_threshold_s
    self._tracks: Dict[str, TrackState] = {}

  def add_fence(self, fence_id: int, geometry) -> None:
    fr = FenceRuntime(id=fence_id, geometry=geometry, prepared=prep(geometry))
    self._fences[fence_id] = fr
    if self._idx:
      self._idx.insert(fence_id, geometry.bounds)

  def remove_fence(self, fence_id: int) -> None:
    fr = self._fences.pop(fence_id, None)
    if fr and self._idx:
      try:
        self._idx.delete(fence_id, fr.geometry.bounds)
      except Exception:
        pass

  def update_position(self, track_id: str, lat: float, lon: float, ts: Optional[float] = None) -> Dict[str, List[Dict]]:
    ts = ts or time.time()
    pt = Point(lon, lat)
    track = self._tracks.setdefault(track_id, TrackState())

    # Candidate fences
    candidates = list(self._fences.keys())
    if self._idx:
      candidates = list(self._idx.intersection((pt.x, pt.y, pt.x, pt.y)))

    entries: List[Dict] = []
    exits: List[Dict] = []
    dwells: List[Dict] = []

    currently_inside: Dict[int, float] = {}
    for fid in candidates:
      fr = self._fences[fid]
      if fr.prepared.contains(pt):
        enter_ts = track.inside.get(fid) or ts
        currently_inside[fid] = enter_ts
        if fid not in track.inside:
          entries.append({"fence_id": fid, "time": ts})
        else:
          dwell = ts - enter_ts
          if dwell >= self._dwell_threshold_s:
            dwells.append({"fence_id": fid, "dwell_s": dwell})

    # Exits are fences previously inside but not in currently_inside
    for fid, enter_ts in list(track.inside.items()):
      if fid not in currently_inside:
        exits.append({"fence_id": fid, "time": ts, "duration_s": ts - enter_ts})

    track.inside = currently_inside
    track.last_point = (lat, lon)
    track.last_ts = ts

    return {"entries": entries, "exits": exits, "dwells": dwells}

  def report_time_spent(self, track_id: str) -> List[Dict]:
    # Best-effort; requires additional state for historical durations in production
    track = self._tracks.get(track_id)
    if not track:
      return []
    res: List[Dict] = []
    now = time.time()
    for fid, enter_ts in track.inside.items():
      res.append({"fence_id": fid, "active_s": now - enter_ts})
    return res

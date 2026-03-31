"""Geofence CRUD and operations.

Manages geofences (circle, polygon, route-based), validation, grouping, and
helpers to persist to a PostGIS-ready form (WKT/GeoJSON). Uses Shapely for
geometry operations. Actual DB storage is performed by callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import Point, Polygon, LineString
from shapely.validation import explain_validity


@dataclass
class GeofenceDef:
  id: Optional[int]
  name: str
  type: str  # circle|polygon|route
  geometry: Any
  properties: Dict[str, Any] = field(default_factory=dict)  # radius for circle, etc.
  group: Optional[str] = None  # e.g., "customer_sites"
  parent_id: Optional[int] = None  # nested fences


class GeofenceManager:
  def __init__(self) -> None:
    self._fences: Dict[int, GeofenceDef] = {}
    self._next_id = 1

  # ---------------------
  # Creation
  # ---------------------
  def create_circle(self, name: str, center_lat: float, center_lng: float, radius_m: float, *, group: Optional[str] = None, parent_id: Optional[int] = None) -> GeofenceDef:
    if radius_m <= 0:
      raise ValueError("radius must be positive")
    geom = Point(center_lng, center_lat).buffer(radius_m / 111_320.0)  # approx deg per meter
    gf = GeofenceDef(id=self._next_id, name=name, type="circle", geometry=geom, properties={"center": (center_lat, center_lng), "radius_m": radius_m}, group=group, parent_id=parent_id)
    self._store(gf)
    return gf

  def create_polygon(self, name: str, coordinates: List[Tuple[float, float]], *, group: Optional[str] = None, parent_id: Optional[int] = None) -> GeofenceDef:
    # coordinates as [(lat, lon), ...]
    if len(coordinates) < 3:
      raise ValueError("polygon requires at least 3 points")
    poly = Polygon([(lng, lat) for lat, lng in coordinates])
    if not poly.is_valid:
      raise ValueError(f"invalid polygon: {explain_validity(poly)}")
    gf = GeofenceDef(id=self._next_id, name=name, type="polygon", geometry=poly, properties={}, group=group, parent_id=parent_id)
    self._store(gf)
    return gf

  def create_route(self, name: str, path: List[Tuple[float, float]], *, buffer_m: float = 50.0, group: Optional[str] = None, parent_id: Optional[int] = None) -> GeofenceDef:
    if len(path) < 2:
      raise ValueError("route requires at least 2 points")
    line = LineString([(lng, lat) for lat, lng in path])
    geom = line.buffer(buffer_m / 111_320.0)
    gf = GeofenceDef(id=self._next_id, name=name, type="route", geometry=geom, properties={"buffer_m": buffer_m}, group=group, parent_id=parent_id)
    self._store(gf)
    return gf

  # ---------------------
  # Update/Delete
  # ---------------------
  def update(self, fence_id: int, **updates: Any) -> GeofenceDef:
    gf = self._require(fence_id)
    for k, v in updates.items():
      if k == "name":
        gf.name = str(v)
      elif k == "group":
        gf.group = str(v) if v is not None else None
      elif k == "parent_id":
        gf.parent_id = int(v) if v is not None else None
      elif k == "geometry":
        if not hasattr(v, "is_valid") or not v.is_valid:
          raise ValueError("invalid geometry")
        gf.geometry = v
      elif k == "properties":
        gf.properties = dict(v or {})
    self._fences[fence_id] = gf
    return gf

  def delete(self, fence_id: int) -> None:
    self._fences.pop(fence_id, None)

  # ---------------------
  # Query/Groups
  # ---------------------
  def list(self, group: Optional[str] = None) -> List[GeofenceDef]:
    if group is None:
      return list(self._fences.values())
    return [g for g in self._fences.values() if g.group == group]

  def children_of(self, parent_id: int) -> List[GeofenceDef]:
    return [g for g in self._fences.values() if g.parent_id == parent_id]

  # ---------------------
  # Storage helpers (PostGIS-ready)
  # ---------------------
  @staticmethod
  def to_wkt(gf: GeofenceDef) -> str:
    return gf.geometry.wkt

  @staticmethod
  def to_geojson(gf: GeofenceDef) -> Dict[str, Any]:
    from shapely.geometry import mapping
    gj = mapping(gf.geometry)
    gj["properties"] = {"name": gf.name, **gf.properties}
    return gj

  # ---------------------
  # Internals
  # ---------------------
  def _store(self, gf: GeofenceDef) -> None:
    gf.id = self._next_id
    self._fences[self._next_id] = gf
    self._next_id += 1

  def _require(self, fence_id: int) -> GeofenceDef:
    if fence_id not in self._fences:
      raise KeyError("geofence not found")
    return self._fences[fence_id]

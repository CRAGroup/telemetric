"""GPS data collection and tracking utilities.

Provides `GpsTracker` which can read GPS data from gpsd (if available) or
parse NMEA sentences via pynmea2, compute speed/heading, detect stops, check
geofences, track distance traveled, and handle signal loss gracefully.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Optional, Tuple
from collections import deque

try:
    import gps  # gpsd python library
except Exception:
    gps = None  # type: ignore

try:
    import pynmea2  # type: ignore
except Exception:
    pynmea2 = None  # type: ignore


@dataclass
class GpsConfig:
    use_gpsd: bool = True
    gpsd_host: str = "127.0.0.1"
    gpsd_port: int = 2947
    stop_speed_kph: float = 5.0
    stop_duration_s: float = 120.0
    max_history: int = 2048


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlambda)
    brng = math.degrees(math.atan2(y, x))
    return (brng + 360.0) % 360.0


class GpsTracker:
    def __init__(self, config: Optional[GpsConfig] = None) -> None:
        self.config = config or GpsConfig()
        self._session = None
        self._history: Deque[Tuple[float, float, float, float]] = deque(maxlen=self.config.max_history)
        # entries are (ts, lat, lon, speed_kph)
        self._stopped_since_ts: Optional[float] = None
        self._distance_km: float = 0.0
        self._last_fix: Optional[Dict] = None

    def connect(self) -> bool:
        if self.config.use_gpsd and gps is not None:
            try:
                self._session = gps.gps(host=self.config.gpsd_host, port=self.config.gpsd_port)
                self._session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
                return True
            except Exception:
                self._session = None
        return False

    def disconnect(self) -> None:
        try:
            if self._session is not None:
                self._session.close()
        except Exception:
            pass
        finally:
            self._session = None

    def _parse_nmea(self, sentence: str) -> Optional[Dict]:
        if pynmea2 is None:
            return None
        try:
            msg = pynmea2.parse(sentence)
            data: Dict = {}
            if hasattr(msg, "latitude") and hasattr(msg, "longitude"):
                data["lat"] = float(msg.latitude)
                data["lon"] = float(msg.longitude)
            if hasattr(msg, "altitude") and msg.altitude:
                try:
                    data["alt_m"] = float(msg.altitude)
                except Exception:
                    pass
            # speed in knots -> kph
            if hasattr(msg, "speed") and msg.speed:
                try:
                    data["speed_kph"] = float(msg.speed) * 1.852
                except Exception:
                    pass
            if hasattr(msg, "true_course") and msg.true_course:
                try:
                    data["heading_deg"] = float(msg.true_course)
                except Exception:
                    pass
            return data if data else None
        except Exception:
            return None

    def _update_state(self, lat: float, lon: float, speed_kph: Optional[float]) -> None:
        now = time.time()
        if self._history:
            _, last_lat, last_lon, last_speed = self._history[-1]
            if speed_kph is None and last_speed is not None:
                speed_kph = last_speed
            self._distance_km += haversine_km(last_lat, last_lon, lat, lon)
        self._history.append((now, lat, lon, speed_kph or 0.0))

        # Stop detection
        current_speed = speed_kph or 0.0
        if current_speed < self.config.stop_speed_kph:
            if self._stopped_since_ts is None:
                self._stopped_since_ts = now
        else:
            self._stopped_since_ts = None

    def _geofence_check(self, fences: Iterable[Dict]) -> List[Dict]:
        res: List[Dict] = []
        if not self._last_fix:
            return res
        lat = self._last_fix.get("lat")
        lon = self._last_fix.get("lon")
        if lat is None or lon is None:
            return res
        for f in fences:
            try:
                center = f.get("center")  # (lat, lon)
                radius_m = float(f.get("radius_m", 0))
                if not center or radius_m <= 0:
                    continue
                d_km = haversine_km(lat, lon, center[0], center[1])
                inside = (d_km * 1000.0) <= radius_m
                res.append({"id": f.get("id"), "inside": inside, "distance_m": d_km * 1000.0})
            except Exception:
                continue
        return res

    def read_from_gpsd(self) -> Optional[Dict]:
        if self._session is None:
            return None
        try:
            report = self._session.next()
            # TPV reports contain fix info
            if report["class"] != "TPV":
                return None
            lat = getattr(report, "lat", None)
            lon = getattr(report, "lon", None)
            alt = getattr(report, "alt", None)
            speed = getattr(report, "speed", None)  # m/s
            track = getattr(report, "track", None)
            epx = getattr(report, "epx", None)
            epy = getattr(report, "epy", None)
            epv = getattr(report, "epv", None)
            if lat is None or lon is None:
                return None
            speed_kph = float(speed) * 3.6 if speed is not None else None
            fix = {
                "lat": float(lat),
                "lon": float(lon),
                "alt_m": float(alt) if alt is not None else None,
                "speed_kph": speed_kph,
                "heading_deg": float(track) if track is not None else None,
                "accuracy_m": float(max(v for v in [epx, epy, epv] if v is not None)) if any(v is not None for v in [epx, epy, epv]) else None,
            }
            self._last_fix = fix
            self._update_state(fix["lat"], fix["lon"], fix["speed_kph"])
            return fix
        except Exception:
            return None

    def read_from_nmea(self, sentence: str) -> Optional[Dict]:
        data = self._parse_nmea(sentence)
        if not data or "lat" not in data or "lon" not in data:
            return None
        # Compute heading from last point if not in sentence
        if "heading_deg" not in data and self._history:
            _, last_lat, last_lon, _ = self._history[-1]
            data["heading_deg"] = bearing_deg(last_lat, last_lon, data["lat"], data["lon"])  # type: ignore[arg-type]
        self._last_fix = data
        self._update_state(data["lat"], data["lon"], data.get("speed_kph"))
        return data

    def get_status(self, geofences: Optional[Iterable[Dict]] = None) -> Dict:
        now = time.time()
        stopped = False
        if self._stopped_since_ts is not None:
            stopped = (now - self._stopped_since_ts) >= self.config.stop_duration_s

        # compute heading from last two points if missing
        heading = None
        if len(self._history) >= 2:
            _, lat1, lon1, _ = self._history[-2]
            _, lat2, lon2, _ = self._history[-1]
            heading = bearing_deg(lat1, lon1, lat2, lon2)

        fix = self._last_fix or {}
        geofence_report = self._geofence_check(geofences or [])
        return {
            "timestamp": now,
            "lat": fix.get("lat"),
            "lon": fix.get("lon"),
            "alt_m": fix.get("alt_m"),
            "speed_kph": fix.get("speed_kph"),
            "heading_deg": fix.get("heading_deg", heading),
            "accuracy_m": fix.get("accuracy_m"),
            "stopped": stopped,
            "distance_km": round(self._distance_km, 5),
            "geofences": geofence_report,
            "has_fix": bool(fix),
        }

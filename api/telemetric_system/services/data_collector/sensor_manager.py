"""Sensor management and dispatch.

`SensorManager` orchestrates OBD and GPS data collectors, schedules polling,
merges their outputs, validates quality, smooths noisy values, monitors health,
and emits unified telemetry packets suitable for storage or streaming.
"""

from __future__ import annotations

import statistics
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional

from .obd_reader import ObdReader, ObdConfig
from .gps_tracker import GpsTracker, GpsConfig


@dataclass
class SensorManagerConfig:
    interval_s: float = 1.0
    smoothing_window: int = 5  # number of samples
    max_buffer: int = 1024


class SensorManager:
    def __init__(
        self,
        obd: Optional[ObdReader] = None,
        gps: Optional[GpsTracker] = None,
        config: Optional[SensorManagerConfig] = None,
    ) -> None:
        self.config = config or SensorManagerConfig()
        self.obd = obd or ObdReader(ObdConfig())
        self.gps = gps or GpsTracker(GpsConfig())

        self._history_speed_kph: Deque[float] = deque(maxlen=self.config.smoothing_window)
        self._history_engine_temp_c: Deque[float] = deque(maxlen=self.config.smoothing_window)
        self._packets: Deque[Dict] = deque(maxlen=self.config.max_buffer)

        # health
        self._last_obd_ts: Optional[float] = None
        self._last_gps_ts: Optional[float] = None

    # ------------------------
    # Lifecycle
    # ------------------------
    def start(self) -> None:
        self.obd.connect()
        self.gps.connect()

    def stop(self) -> None:
        self.obd.disconnect()
        self.gps.disconnect()

    # ------------------------
    # Scheduling
    # ------------------------
    def poll_once(self) -> Dict:
        now = time.time()

        # OBD
        obd_reading = self.obd.read_parameters()
        self._last_obd_ts = now

        # GPS (prefer gpsd continuous; fallback assumes external call updated last fix)
        gps_fix = self.gps.read_from_gpsd() or self.gps.get_status()
        self._last_gps_ts = now

        packet = self._merge_and_validate(obd_reading, gps_fix)
        packet = self._smooth(packet)
        self._packets.append(packet)
        return packet

    def run_loop(self) -> None:
        try:
            self.start()
            while True:
                started = time.time()
                self.poll_once()
                elapsed = time.time() - started
                sleep_for = max(0.0, self.config.interval_s - elapsed)
                time.sleep(sleep_for)
        finally:
            self.stop()

    # ------------------------
    # Merging / validation / smoothing
    # ------------------------
    def _merge_and_validate(self, obd_reading: Dict, gps_fix: Dict) -> Dict:
        # Basic merge
        obd_data = obd_reading.get("obd", {}) if isinstance(obd_reading, dict) else {}
        gps_fields = {
            "lat": gps_fix.get("lat"),
            "lon": gps_fix.get("lon"),
            "alt_m": gps_fix.get("alt_m"),
            "speed_kph": gps_fix.get("speed_kph"),
            "heading_deg": gps_fix.get("heading_deg"),
            "accuracy_m": gps_fix.get("accuracy_m"),
            "stopped": gps_fix.get("stopped"),
            "distance_km": gps_fix.get("distance_km"),
        }

        # Data quality checks
        quality: List[str] = []
        lat = gps_fields["lat"]
        lon = gps_fields["lon"]
        if lat is not None and not (-90.0 <= lat <= 90.0):
            quality.append("gps_lat_out_of_range")
        if lon is not None and not (-180.0 <= lon <= 180.0):
            quality.append("gps_lon_out_of_range")
        speed_kph = gps_fields["speed_kph"]
        if speed_kph is not None and speed_kph < 0:
            quality.append("gps_speed_negative")
        rpm = obd_data.get("rpm")
        if rpm is not None and rpm < 0:
            quality.append("obd_rpm_negative")

        timestamp = time.time()
        packet = {
            "timestamp": timestamp,
            "vehicle": {
                "lat": lat,
                "lon": lon,
                "alt_m": gps_fields["alt_m"],
                "speed_kph": speed_kph,
                "heading_deg": gps_fields["heading_deg"],
                "accuracy_m": gps_fields["accuracy_m"],
                "stopped": gps_fields["stopped"],
                "distance_km": gps_fields["distance_km"],
            },
            "engine": {
                "rpm": obd_data.get("rpm"),
                "engine_temp_c": obd_data.get("coolant_temp_c"),
                "engine_load_pct": obd_data.get("engine_load_pct"),
                "throttle_pos_pct": obd_data.get("throttle_pos_pct"),
                "fuel_level_pct": obd_data.get("fuel_level_pct"),
                "battery_voltage_v": obd_data.get("battery_voltage_v"),
            },
            "quality": quality,
        }
        return packet

    def _smooth(self, packet: Dict) -> Dict:
        # smooth speed
        speed = packet["vehicle"].get("speed_kph")
        if isinstance(speed, (int, float)):
            self._history_speed_kph.append(float(speed))
            packet["vehicle"]["speed_kph_smoothed"] = round(statistics.fmean(self._history_speed_kph), 3)
        # smooth engine temp
        engine_temp = packet["engine"].get("engine_temp_c")
        if isinstance(engine_temp, (int, float)):
            self._history_engine_temp_c.append(float(engine_temp))
            packet["engine"]["engine_temp_c_smoothed"] = round(statistics.fmean(self._history_engine_temp_c), 3)
        return packet

    # ------------------------
    # Health
    # ------------------------
    def health(self) -> Dict:
        now = time.time()
        return {
            "obd_connected": self.obd.is_connected(),
            "gps_connected": self.gps._session is not None,  # best effort
            "last_obd_s": None if self._last_obd_ts is None else (now - self._last_obd_ts),
            "last_gps_s": None if self._last_gps_ts is None else (now - self._last_gps_ts),
            "buffered_packets": len(self._packets),
        }

    def get_packets(self, limit: int = 100) -> List[Dict]:
        if limit <= 0:
            return []
        return list(self._packets)[-limit:]

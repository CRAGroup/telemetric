"""OBD-II data reading and parsing.

Provides `ObdReader` which:
- Connects to an OBD-II adapter via python-OBD
- Reads engine parameters (RPM, speed, fuel level, coolant temp, etc.)
- Retrieves diagnostic trouble codes (DTCs)
- Handles connection errors with retries and backoff
- Buffers readings when offline and flushes on reconnect
- Returns standardized dict format for telemetry ingestion
"""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional

try:
    import obd  # type: ignore
    from obd import OBDStatus
    from obd import commands as OBD
except Exception:  # pragma: no cover - library optional at dev time
    obd = None
    OBDStatus = None
    OBD = None


@dataclass
class ObdConfig:
    port: Optional[str] =  "/dev/ttyUSB0"  # e.g., "/dev/ttyUSB0" or COM3
    baudrate: Optional[int] = None
    fast: bool = True
    timeout_s: float = 5.0
    max_retries: int = 5
    backoff_s: float = 1.0
    max_buffer: int = 1000


class ObdReader:
    def __init__(self, config: Optional[ObdConfig] = None) -> None:
        self.config = config or ObdConfig()
        self._conn = None
        self._buffer: Deque[Dict] = deque(maxlen=self.config.max_buffer)

    # --------------------
    # Connection handling
    # --------------------
    def connect(self) -> bool:
        if obd is None:
            return False
        for attempt in range(1, self.config.max_retries + 1):
            try:
                self._conn = obd.OBD(
                    portstr=self.config.port,
                   # baudrate=self.config.baudrate,
                    fast=self.config.fast,
                   # timeout=self.config.timeout_s,
                )
                if self._conn.status() == OBDStatus.CAR_CONNECTED or self._conn.is_connected():
                    return True
            except Exception:
                pass
            time.sleep(self.config.backoff_s * attempt)
        return False

    def disconnect(self) -> None:
        try:
            if self._conn is not None:
                self._conn.close()
        finally:
            self._conn = None

    def is_connected(self) -> bool:
        try:
            return bool(self._conn and (self._conn.is_connected() or self._conn.status() == OBDStatus.CAR_CONNECTED))
        except Exception:
            return False

    # --------------------
    # Reading helpers
    # --------------------
    def _safe_query(self, cmd) -> Optional[float]:
        try:
            if not self.is_connected():
                return None
            r = self._conn.query(cmd)  # type: ignore[attr-defined]
            if r is not None and not r.is_null():
                # Many python-OBD values have .value.magnitude or .value.to("unit")
                v = r.value
                if hasattr(v, "magnitude"):
                    return float(v.magnitude)
                try:
                    return float(v)
                except Exception:
                    return None
            return None
        except Exception:
            return None

    def read_parameters(self) -> Dict:
        """Read a set of engine/vehicle parameters in a standardized dict.

        When offline, store a placeholder reading in the buffer and return last known values if any.
        """
        data = {
            "rpm": self._safe_query(OBD.RPM) if OBD else None,
            "speed_kph": self._safe_query(OBD.SPEED) if OBD else None,
            "fuel_level_pct": self._safe_query(OBD.FUEL_LEVEL) if OBD else None,
            "coolant_temp_c": self._safe_query(OBD.COOLANT_TEMP) if OBD else None,
            "engine_load_pct": self._safe_query(OBD.ENGINE_LOAD) if OBD else None,
            "throttle_pos_pct": self._safe_query(OBD.THROTTLE_POS) if OBD else None,
            "intake_temp_c": self._safe_query(OBD.INTAKE_TEMP) if OBD else None,
            "maf_gps": self._safe_query(OBD.MAF) if OBD else None,
            "barometric_kpa": self._safe_query(OBD.BAROMETRIC_PRESSURE) if OBD else None,
            "fuel_status" : self._safe_query(OBD.FUEL_STATUS) if OBD else None,
            "engine_runtime": self._safe_query(OBD.RUN_TIME) if OBD else None,
            "engine_oil_temperature": self._safe_query(OBD.OIL_TEMP) if OBD else None,        }

        if not self.is_connected():
            # buffer an offline marker
            self._buffer.append({"offline": True, "data": data, "ts": time.time()})
        else:
            # store last good read in buffer
            self._buffer.append({"offline": False, "data": data, "ts": time.time()})

        return {
            "timestamp": time.time(),
            "obd": data,
            "buffered": len(self._buffer),
        }

    def get_dtc_codes(self) -> List[str]:
        try:
            if not self.is_connected() or OBD is None:
                return []
            r = self._conn.query(OBD.GET_DTC)  # type: ignore[attr-defined]
            if r is None or r.is_null():
                return []
            # python-OBD returns list of tuples (code, description)
            codes = []
            try:
                for item in r.value:  # type: ignore[attr-defined]
                    if isinstance(item, (list, tuple)) and item:
                        codes.append(str(item[0]))
            except Exception:
                pass
            return codes
        except Exception:
            return []

    # --------------------
    # Buffer management
    # --------------------
    def flush_buffer(self) -> List[Dict]:
        """Return and clear the buffered readings."""
        items = list(self._buffer)
        self._buffer.clear()
        return items

    def to_json(self, reading: Dict) -> str:
        return json.dumps(reading, separators=(",", ":"))

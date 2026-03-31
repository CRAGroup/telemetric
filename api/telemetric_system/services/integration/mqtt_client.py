
"""MQTT client for device communication.

Provides `MqttClient` that:
- Connects to broker with optional authentication and TLS
- Auto-reconnects with exponential backoff
- Subscribes to telemetry topics: vehicles/{vehicle_id}/{data_type}
- Publishes commands to vehicles with configurable QoS and retain
- Buffers outgoing messages when offline and flushes on reconnect
- Logs all MQTT events
"""

from __future__ import annotations

import json
import logging
import ssl
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional

try:
    import paho.mqtt.client as mqtt  # type: ignore
except Exception:  # pragma: no cover
    mqtt = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class MqttConfig:
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = False
    ca_cert: Optional[str] = None
    client_id: Optional[str] = None
    keepalive: int = 60
    qos: int = 1  # default QoS
    max_buffer: int = 1000


class MqttClient:
    def __init__(self, config: MqttConfig) -> None:
        self.config = config
        self._client = mqtt.Client(client_id=config.client_id) if mqtt else None
        self._connected = False
        self._out_buffer: Deque[Dict] = deque(maxlen=config.max_buffer)
        self._backoff = 1.0
        self._max_backoff = 60.0

        if self._client:
            if self.config.username and self.config.password:
                self._client.username_pw_set(self.config.username, self.config.password)
            if self.config.use_tls:
                if self.config.ca_cert:
                    self._client.tls_set(ca_certs=self.config.ca_cert, certfile=None, keyfile=None, tls_version=ssl.PROTOCOL_TLS)
                else:
                    self._client.tls_set(tls_version=ssl.PROTOCOL_TLS)

            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message
            self._client.on_subscribe = self._on_subscribe
            self._client.on_publish = self._on_publish

    # ------------------
    # Connection
    # ------------------
    def connect(self) -> None:
        if not self._client:
            logger.warning("paho-mqtt not available; MQTT disabled")
            return
        try:
            logger.info("MQTT connecting to %s:%s", self.config.host, self.config.port)
            self._client.connect(self.config.host, self.config.port, keepalive=self.config.keepalive)
            self._client.loop_start()
        except Exception as exc:
            logger.exception("MQTT initial connect failed: %s", exc)
            self._schedule_reconnect()

    def disconnect(self) -> None:
        try:
            if self._client:
                self._client.loop_stop()
                self._client.disconnect()
        finally:
            self._connected = False

    def _schedule_reconnect(self) -> None:
        if not self._client:
            return
        delay = min(self._backoff, self._max_backoff)
        logger.warning("MQTT reconnect in %.1fs", delay)
        time.sleep(delay)
        self._backoff *= 2
        try:
            self._client.reconnect()
        except Exception:
            self._schedule_reconnect()

    # ------------------
    # Callbacks
    # ------------------
    def _on_connect(self, client, userdata, flags, rc):  # noqa: ANN001, D401, N802
        self._connected = (rc == 0)
        self._backoff = 1.0
        if self._connected:
            logger.info("MQTT connected (rc=%s)", rc)
            self._flush_buffer()
        else:
            logger.error("MQTT connect error rc=%s", rc)
            self._schedule_reconnect()

    def _on_disconnect(self, client, userdata, rc):  # noqa: ANN001, D401, N802
        logger.warning("MQTT disconnected rc=%s", rc)
        self._connected = False
        if rc != 0:
            self._schedule_reconnect()

    def _on_message(self, client, userdata, msg):  # noqa: ANN001, D401, N802
        logger.info("MQTT message topic=%s qos=%s payload=%s", msg.topic, msg.qos, msg.payload)

    def _on_subscribe(self, client, userdata, mid, granted_qos):  # noqa: ANN001, D401, N802
        logger.info("MQTT subscribed mid=%s qos=%s", mid, granted_qos)

    def _on_publish(self, client, userdata, mid):  # noqa: ANN001, D401, N802
        logger.debug("MQTT published mid=%s", mid)

    # ------------------
    # Topics
    # ------------------
    @staticmethod
    def telemetry_topic(vehicle_id: str, data_type: str) -> str:
        return f"vehicles/{vehicle_id}/{data_type}"

    @staticmethod
    def command_topic(vehicle_id: str) -> str:
        return f"vehicles/{vehicle_id}/commands"

    # ------------------
    # Subscribe/Publish
    # ------------------
    def subscribe_vehicle(self, vehicle_id: str, data_type: str, qos: Optional[int] = None) -> None:
        if not self._client:
            return
        topic = self.telemetry_topic(vehicle_id, data_type)
        q = self._normalize_qos(qos)
        logger.info("MQTT subscribe %s qos=%s", topic, q)
        self._client.subscribe(topic, qos=q)

    def publish_command(self, vehicle_id: str, payload: Dict, qos: Optional[int] = None, retain: bool = False) -> None:
        topic = self.command_topic(vehicle_id)
        self.publish(topic, payload, qos=qos, retain=retain)

    def publish(self, topic: str, payload: Dict, qos: Optional[int] = None, retain: bool = False) -> None:
        message = json.dumps(payload, separators=(",", ":"))
        q = self._normalize_qos(qos)
        if not self._client or not self._connected:
            logger.warning("MQTT offline, buffering topic=%s", topic)
            self._out_buffer.append({"topic": topic, "message": message, "qos": q, "retain": retain})
            return
        result = self._client.publish(topic, message, qos=q, retain=retain)
        if result.rc != mqtt.MQTT_ERR_SUCCESS:  # type: ignore[attr-defined]
            logger.error("MQTT publish failed rc=%s; buffering", result.rc)
            self._out_buffer.append({"topic": topic, "message": message, "qos": q, "retain": retain})

    def _flush_buffer(self) -> None:
        if not self._client or not self._connected:
            return
        while self._out_buffer:
            item = self._out_buffer.popleft()
            logger.info("MQTT flushing buffered topic=%s", item["topic"])
            self._client.publish(item["topic"], item["message"], qos=item["qos"], retain=item["retain"])  # type: ignore[arg-type]

    @staticmethod
    def _normalize_qos(qos: Optional[int]) -> int:
        if qos is None:
            return 1
        if qos not in (0, 1, 2):
            return 1
        return qos

from __future__ import annotations

import json
import random
import time
from datetime import datetime

from locust import HttpUser, task, between


VEHICLE_IDS = [i for i in range(1, 1001)]


class ApiUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task(3)
    def post_telemetry(self):
        vid = random.choice(VEHICLE_IDS)
        payload = {
            "vehicle_id": vid,
            "timestamp": time.time(),
            "vehicle": {"lat": -1.28 + random.random() * 0.1, "lon": 36.8 + random.random() * 0.1, "speed_kph": random.random() * 120},
            "engine": {"rpm": int(random.random() * 4000), "engine_temp_c": 80 + random.random() * 40},
        }
        self.client.post("/telemetry", json=payload, headers={"Authorization": "Bearer TEST"})

    @task(1)
    def list_vehicles(self):
        self.client.get("/vehicles?page=1&page_size=50", headers={"Authorization": "Bearer TEST"})

    @task(1)
    def analytics_overview(self):
        self.client.get("/analytics/fleet-overview", headers={"Authorization": "Bearer TEST"})


# WebSocket and DB write performance can be measured via separate tools or locust plugins.
# For WS, consider locust-plugins websocket user or a separate artillery/k6 scenario.

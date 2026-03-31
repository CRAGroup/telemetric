"""Route registration for REST endpoints."""

from telemetric_system.api.routes import vehicles, drivers, telemetry, analytics, reports, auth, alerts, geofence as geofences

__all__ = [
    "vehicles",
    "drivers",
    "telemetry",
    "analytics",
    "reports",
    "auth",
    "alerts",
    "geofences",
]


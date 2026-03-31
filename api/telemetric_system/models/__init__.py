"""ORM models for relational/time-series/document stores."""

from telemetric_system.models.base import Base, BaseModel
from telemetric_system.models.user import User
from telemetric_system.models.vehicle_type import VehicleType
from telemetric_system.models.vehicle import Vehicle
from telemetric_system.models.driver import Driver
from telemetric_system.models.telemetry import Telemetry
from telemetric_system.models.trip import Trip
from telemetric_system.models.alert import Alert
from telemetric_system.models.geofence import Geofence, vehicle_geofences
from telemetric_system.models.maintenance import MaintenanceRecord
from telemetric_system.models.fuel import FuelTransaction
from telemetric_system.models.admin_settings import AdminSettings

__all__ = [
  "Base",
  "BaseModel",
  "User",
  "VehicleType",
  "Vehicle",
  "Driver",
  "Telemetry",
  "Trip",
  "Alert",
  "Geofence",
  "vehicle_geofences",
  "MaintenanceRecord",
  "FuelTransaction",
  "AdminSettings",
]


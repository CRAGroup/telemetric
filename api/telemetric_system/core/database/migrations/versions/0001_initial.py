"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-13
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=120)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="viewer"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # drivers
    op.create_table(
        "drivers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("driver_identifier", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("license_number", sa.String(length=64), nullable=False),
        sa.Column("license_expiry", sa.Date()),
        sa.Column("phone_number", sa.String(length=32)),
        sa.Column("email", sa.String(length=120)),
        sa.UniqueConstraint("driver_identifier"),
        sa.UniqueConstraint("license_number"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_drivers_driver_identifier", "drivers", ["driver_identifier"], unique=True)

    # vehicles
    op.create_table(
        "vehicles",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.String(length=50), nullable=False),
        sa.Column("registration_number", sa.String(length=32), nullable=False),
        sa.Column("make", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("vin_number", sa.String(length=64)),
        sa.Column("current_odometer", sa.Float(), nullable=False, server_default="0"),
        sa.Column("fuel_tank_capacity", sa.Float()),
        sa.Column("driver_id", sa.BigInteger(), sa.ForeignKey("drivers.id", ondelete="SET NULL")),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("device_imei", sa.String(length=32)),
        sa.UniqueConstraint("vehicle_id"),
        sa.UniqueConstraint("registration_number"),
        sa.UniqueConstraint("vin_number"),
    )
    op.create_index("ix_vehicles_vehicle_id", "vehicles", ["vehicle_id"], unique=True)
    op.create_index("ix_vehicles_registration_number", "vehicles", ["registration_number"], unique=True)

    # vehicle_geofences
    op.create_table(
        "geofences",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512)),
        sa.Column("center_lat", sa.Float(), nullable=False),
        sa.Column("center_lng", sa.Float(), nullable=False),
        sa.Column("radius_m", sa.Float(), nullable=False),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_geofences_name", "geofences", ["name"], unique=True)

    op.create_table(
        "vehicle_geofences",
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("geofence_id", sa.BigInteger(), sa.ForeignKey("geofences.id", ondelete="CASCADE"), primary_key=True),
    )

    # telemetry_data
    op.create_table(
        "telemetry_data",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", sa.BigInteger(), sa.ForeignKey("drivers.id", ondelete="SET NULL")),
        sa.Column("timestamp_utc", sa.DateTime(timezone=False), nullable=False),
        sa.Column("rpm", sa.Integer()),
        sa.Column("engine_temp_c", sa.Float()),
        sa.Column("oil_pressure_kpa", sa.Float()),
        sa.Column("battery_voltage_v", sa.Float()),
        sa.Column("throttle_pos_pct", sa.Float()),
        sa.Column("engine_load_pct", sa.Float()),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("speed_kph", sa.Float()),
        sa.Column("heading_deg", sa.Float()),
        sa.Column("altitude_m", sa.Float()),
        sa.Column("fuel_level_pct", sa.Float()),
        sa.Column("fuel_rate_lph", sa.Float()),
        sa.Column("harsh_accel", sa.Boolean()),
        sa.Column("hard_brake", sa.Boolean()),
        sa.Column("sharp_corner", sa.Boolean()),
        sa.Column("speeding", sa.Boolean()),
        sa.Column("seatbelt_used", sa.Boolean()),
    )

    # alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", sa.BigInteger(), sa.ForeignKey("drivers.id", ondelete="SET NULL")),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=500)),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="warning"),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True)),
        sa.Column("rule_id", sa.String(length=64)),
    )

    # maintenance_records
    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("odometer_km", sa.Float()),
        sa.Column("service_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=500)),
        sa.Column("cost", sa.Float()),
    )

    # fuel_transactions
    op.create_table(
        "fuel_transactions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_time_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("liters", sa.Float(), nullable=False),
        sa.Column("price_per_liter", sa.Float()),
        sa.Column("station_name", sa.String(length=128)),
        sa.Column("note", sa.String(length=500)),
    )

    # trips
    op.create_table(
        "trips",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("vehicle_id", sa.BigInteger(), sa.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("driver_id", sa.BigInteger(), sa.ForeignKey("drivers.id", ondelete="SET NULL")),
        sa.Column("start_time_utc", sa.DateTime(timezone=False), nullable=False),
        sa.Column("end_time_utc", sa.DateTime(timezone=False)),
        sa.Column("start_lat", sa.Float()),
        sa.Column("start_lng", sa.Float()),
        sa.Column("end_lat", sa.Float()),
        sa.Column("end_lng", sa.Float()),
        sa.Column("distance_km", sa.Float()),
        sa.Column("fuel_used_l", sa.Float()),
    )


def downgrade() -> None:
    op.drop_table("trips")
    op.drop_table("fuel_transactions")
    op.drop_table("maintenance_records")
    op.drop_table("alerts")
    op.drop_table("telemetry_data")
    op.drop_table("vehicle_geofences")
    op.drop_table("geofences")
    op.drop_table("vehicles")
    op.drop_table("drivers")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

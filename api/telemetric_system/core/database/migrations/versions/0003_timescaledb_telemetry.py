"""timescaledb setup for telemetry_data

Revision ID: 0003_timescaledb_telemetry
Revises: 0002_seed_data
Create Date: 2025-10-13
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_timescaledb_telemetry"
down_revision = "0002_seed_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Ensure TimescaleDB extension
    conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb"))

    # Convert telemetry_data to hypertable (if not already)
    # Uses timestamp column 'timestamp_utc'
    conn.execute(
        sa.text(
            "SELECT create_hypertable('telemetry_data', 'timestamp_utc', if_not_exists => TRUE, migrate_data => TRUE)"
        )
    )

    # Recommended indexes for common queries
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_telem_vehicle_time ON telemetry_data (vehicle_id, timestamp_utc DESC)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_telem_driver_time ON telemetry_data (driver_id, timestamp_utc DESC)"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_telem_geo ON telemetry_data (latitude, longitude)"))

    # Compression (Timescale)
    conn.execute(sa.text("ALTER TABLE telemetry_data SET (timescaledb.compress, timescaledb.compress_segmentby = 'vehicle_id')"))
    # Compress chunks older than 7 days
    conn.execute(
        sa.text(
            "SELECT add_compression_policy('telemetry_data', INTERVAL '7 days')"
        )
    )

    # Retention policy: keep 90 days of raw telemetry
    conn.execute(sa.text("SELECT add_retention_policy('telemetry_data', INTERVAL '90 days')"))

    # Continuous aggregates for hourly and daily summaries
    conn.execute(
        sa.text(
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket(INTERVAL '1 hour', timestamp_utc) AS bucket,
                vehicle_id,
                AVG(speed_kph) AS avg_speed_kph,
                MAX(speed_kph) AS max_speed_kph,
                AVG(engine_temp_c) AS avg_engine_temp_c,
                AVG(fuel_level_pct) AS avg_fuel_level_pct
            FROM telemetry_data
            GROUP BY bucket, vehicle_id
            WITH NO DATA;
            """
        )
    )
    conn.execute(
        sa.text(
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_daily
            WITH (timescaledb.continuous) AS
            SELECT
                time_bucket(INTERVAL '1 day', timestamp_utc) AS bucket,
                vehicle_id,
                AVG(speed_kph) AS avg_speed_kph,
                MAX(speed_kph) AS max_speed_kph,
                AVG(engine_temp_c) AS avg_engine_temp_c,
                AVG(fuel_level_pct) AS avg_fuel_level_pct
            FROM telemetry_data
            GROUP BY bucket, vehicle_id
            WITH NO DATA;
            """
        )
    )

    # Refresh policies for continuous aggregates
    conn.execute(
        sa.text(
            "SELECT add_continuous_aggregate_policy('telemetry_hourly', start_offset => INTERVAL '7 days', end_offset => INTERVAL '1 hour', schedule_interval => INTERVAL '1 hour')"
        )
    )
    conn.execute(
        sa.text(
            "SELECT add_continuous_aggregate_policy('telemetry_daily', start_offset => INTERVAL '90 days', end_offset => INTERVAL '1 day', schedule_interval => INTERVAL '1 day')"
        )
    )


def downgrade() -> None:
    conn = op.get_bind()

    # Remove policies and continuous aggregates
    conn.execute(sa.text("SELECT remove_continuous_aggregate_policy('telemetry_hourly')"))
    conn.execute(sa.text("SELECT remove_continuous_aggregate_policy('telemetry_daily')"))
    conn.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS telemetry_daily"))
    conn.execute(sa.text("DROP MATERIALIZED VIEW IF EXISTS telemetry_hourly"))

    # Remove policies and compression
    conn.execute(sa.text("SELECT remove_retention_policy('telemetry_data')"))
    conn.execute(sa.text("SELECT remove_compression_policy('telemetry_data')"))
    conn.execute(sa.text("ALTER TABLE telemetry_data RESET (timescaledb.compress, timescaledb.compress_segmentby)"))
    # Note: hypertable remains; reversing to normal table is non-trivial and typically unnecessary

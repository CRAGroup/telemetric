"""seed data

Revision ID: 0002_seed_data
Revises: 0001_initial
Create Date: 2025-10-13
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = "0002_seed_data"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


users = table(
    "users",
    column("email", sa.String),
    column("hashed_password", sa.String),
    column("full_name", sa.String),
    column("is_active", sa.Boolean),
    column("role", sa.String),
)

# Placeholder sample makes via vehicles table is tricky; instead we insert a sample vehicle
vehicles = table(
    "vehicles",
    column("vehicle_id", sa.String),
    column("registration_number", sa.String),
    column("make", sa.String),
    column("model", sa.String),
    column("year", sa.Integer),
    column("current_odometer", sa.Float),
    column("status", sa.String),
)

# Default alert rules placeholder table is not defined; we use a generic alerts seed for demo
alerts = table(
    "alerts",
    column("vehicle_id", sa.BigInteger),
    column("alert_type", sa.String),
    column("message", sa.String),
    column("severity", sa.String),
)


def upgrade() -> None:
    # default admin user (password should be set securely in real deployments)
    op.bulk_insert(
        users,
        [
            {
                "email": "admin@example.com",
                "hashed_password": "$2b$12$examplehashplaceholder",  # bcrypt hash placeholder
                "full_name": "Administrator",
                "is_active": True,
                "role": "admin",
            }
        ],
    )

    # sample vehicle
    op.bulk_insert(
        vehicles,
        [
            {
                "vehicle_id": "VH-0001",
                "registration_number": "KAA123A",
                "make": "Toyota",
                "model": "Hilux",
                "year": 2020,
                "current_odometer": 0.0,
                "status": "active",
            }
        ],
    )

    # default alert placeholder (requires a valid vehicle id; use subqueryless minimal insert by assuming id=1 in dev)
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM vehicles ORDER BY id ASC LIMIT 1"))
    row = result.fetchone()
    vehicle_id = row[0] if row else None
    if vehicle_id is not None:
        op.bulk_insert(
            alerts,
            [
                {
                    "vehicle_id": vehicle_id,
                    "alert_type": "speed_limit",
                    "message": "Speed exceeds configured limit",
                    "severity": "warning",
                }
            ],
        )


def downgrade() -> None:
    # best-effort deletes
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM alerts WHERE alert_type='speed_limit'"))
    conn.execute(sa.text("DELETE FROM vehicles WHERE vehicle_id='VH-0001'"))
    conn.execute(sa.text("DELETE FROM users WHERE email='admin@example.com'"))

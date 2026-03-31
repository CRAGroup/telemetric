"""Add extended fields to maintenance_records.

Revision ID: 0006
Revises: 0005
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to maintenance_records (ignore if already exist)
    with op.batch_alter_table("maintenance_records") as batch_op:
        try:
            batch_op.add_column(sa.Column("mechanic", sa.String(128), nullable=True))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column("priority", sa.String(20), nullable=True, server_default="medium"))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column("record_type", sa.String(20), nullable=True, server_default="scheduled"))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column("status", sa.String(20), nullable=True, server_default="pending"))
        except Exception:
            pass
        try:
            batch_op.add_column(sa.Column("completed_date", sa.Date(), nullable=True))
        except Exception:
            pass


def downgrade() -> None:
    with op.batch_alter_table("maintenance_records") as batch_op:
        for col in ["mechanic", "priority", "record_type", "status", "completed_date"]:
            try:
                batch_op.drop_column(col)
            except Exception:
                pass

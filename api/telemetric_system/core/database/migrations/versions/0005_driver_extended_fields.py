"""add driver extended fields

Revision ID: 0005
Revises: 0004
Create Date: 2026-03-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to drivers table
    op.add_column('drivers', sa.Column('license_class', sa.String(length=10), nullable=True))
    op.add_column('drivers', sa.Column('national_id', sa.String(length=64), nullable=True))
    op.add_column('drivers', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('blood_group', sa.String(length=10), nullable=True))
    op.add_column('drivers', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('drivers', sa.Column('medical_certificate_expiry', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('psv_badge_number', sa.String(length=64), nullable=True))
    op.add_column('drivers', sa.Column('psv_badge_expiry', sa.Date(), nullable=True))
    op.add_column('drivers', sa.Column('emergency_contact_name', sa.String(length=128), nullable=True))
    op.add_column('drivers', sa.Column('emergency_contact_phone', sa.String(length=32), nullable=True))
    op.add_column('drivers', sa.Column('next_of_kin_name', sa.String(length=128), nullable=True))
    op.add_column('drivers', sa.Column('next_of_kin_phone', sa.String(length=32), nullable=True))
    op.add_column('drivers', sa.Column('next_of_kin_relationship', sa.String(length=64), nullable=True))
    op.add_column('drivers', sa.Column('years_experience', sa.Integer(), nullable=True))
    op.add_column('drivers', sa.Column('previous_employer', sa.String(length=256), nullable=True))
    op.add_column('drivers', sa.Column('status', sa.String(length=20), nullable=True, server_default='active'))
    op.add_column('drivers', sa.Column('avatar_url', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('drivers', 'avatar_url')
    op.drop_column('drivers', 'status')
    op.drop_column('drivers', 'previous_employer')
    op.drop_column('drivers', 'years_experience')
    op.drop_column('drivers', 'next_of_kin_relationship')
    op.drop_column('drivers', 'next_of_kin_phone')
    op.drop_column('drivers', 'next_of_kin_name')
    op.drop_column('drivers', 'emergency_contact_phone')
    op.drop_column('drivers', 'emergency_contact_name')
    op.drop_column('drivers', 'psv_badge_expiry')
    op.drop_column('drivers', 'psv_badge_number')
    op.drop_column('drivers', 'medical_certificate_expiry')
    op.drop_column('drivers', 'address')
    op.drop_column('drivers', 'blood_group')
    op.drop_column('drivers', 'date_of_birth')
    op.drop_column('drivers', 'national_id')
    op.drop_column('drivers', 'license_class')

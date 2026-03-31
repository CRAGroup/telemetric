"""Add Supabase compatibility fields and tables

Revision ID: 0004
Revises: 0003_timescaledb_telemetry
Create Date: 2026-03-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003_timescaledb_telemetry'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vehicle_types table
    op.create_table(
        'vehicle_types',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_vehicle_types_id'), 'vehicle_types', ['id'], unique=False)
    op.create_index(op.f('ix_vehicle_types_is_deleted'), 'vehicle_types', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_vehicle_types_name'), 'vehicle_types', ['name'], unique=False)

    # Create admin_settings table
    op.create_table(
        'admin_settings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('key', sa.String(length=128), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_admin_settings_id'), 'admin_settings', ['id'], unique=False)
    op.create_index(op.f('ix_admin_settings_is_deleted'), 'admin_settings', ['is_deleted'], unique=False)
    op.create_index(op.f('ix_admin_settings_key'), 'admin_settings', ['key'], unique=False)
    op.create_index(op.f('ix_admin_settings_category'), 'admin_settings', ['category'], unique=False)

    # Add new columns to vehicles table
    op.add_column('vehicles', sa.Column('model_name', sa.String(length=128), nullable=True))
    op.add_column('vehicles', sa.Column('max_load_weight', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('current_load_weight', sa.Float(), nullable=True, server_default='0'))
    op.add_column('vehicles', sa.Column('load_category', sa.String(length=64), nullable=True))
    op.add_column('vehicles', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('vehicles', sa.Column('image_url', sa.Text(), nullable=True))
    op.add_column('vehicles', sa.Column('vehicle_type_id', sa.BigInteger(), nullable=True))
    
    # Add foreign key for vehicle_type_id
    op.create_foreign_key(
        'fk_vehicles_vehicle_type_id',
        'vehicles', 'vehicle_types',
        ['vehicle_type_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_vehicles_vehicle_type_id'), 'vehicles', ['vehicle_type_id'], unique=False)

    # Add new status values to vehicle_status enum
    # Note: This requires recreating the enum in PostgreSQL
    # For SQLite, this is a no-op as it doesn't have native enums
    
    # Add check constraints for new fields
    op.create_check_constraint(
        'ck_vehicle_load_nonneg',
        'vehicles',
        'current_load_weight IS NULL OR current_load_weight >= 0'
    )
    op.create_check_constraint(
        'ck_vehicle_max_load_pos',
        'vehicles',
        'max_load_weight IS NULL OR max_load_weight > 0'
    )
    op.create_check_constraint(
        'ck_vehicle_lat_range',
        'vehicles',
        'latitude IS NULL OR (latitude >= -90 AND latitude <= 90)'
    )
    op.create_check_constraint(
        'ck_vehicle_lng_range',
        'vehicles',
        'longitude IS NULL OR (longitude >= -180 AND longitude <= 180)'
    )

    # Seed default vehicle types
    op.execute("""
        INSERT INTO vehicle_types (name, description) VALUES
        ('Truck', 'Heavy duty cargo truck'),
        ('Van', 'Light commercial van'),
        ('Pickup', 'Pickup truck'),
        ('Trailer', 'Semi-trailer truck'),
        ('Tanker', 'Fuel or liquid tanker'),
        ('Refrigerated', 'Refrigerated transport vehicle')
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    # Remove check constraints
    op.drop_constraint('ck_vehicle_lng_range', 'vehicles', type_='check')
    op.drop_constraint('ck_vehicle_lat_range', 'vehicles', type_='check')
    op.drop_constraint('ck_vehicle_max_load_pos', 'vehicles', type_='check')
    op.drop_constraint('ck_vehicle_load_nonneg', 'vehicles', type_='check')
    
    # Remove foreign key and index
    op.drop_index(op.f('ix_vehicles_vehicle_type_id'), table_name='vehicles')
    op.drop_constraint('fk_vehicles_vehicle_type_id', 'vehicles', type_='foreignkey')
    
    # Remove columns from vehicles
    op.drop_column('vehicles', 'vehicle_type_id')
    op.drop_column('vehicles', 'image_url')
    op.drop_column('vehicles', 'longitude')
    op.drop_column('vehicles', 'latitude')
    op.drop_column('vehicles', 'load_category')
    op.drop_column('vehicles', 'current_load_weight')
    op.drop_column('vehicles', 'max_load_weight')
    op.drop_column('vehicles', 'model_name')
    
    # Drop admin_settings table
    op.drop_index(op.f('ix_admin_settings_category'), table_name='admin_settings')
    op.drop_index(op.f('ix_admin_settings_key'), table_name='admin_settings')
    op.drop_index(op.f('ix_admin_settings_is_deleted'), table_name='admin_settings')
    op.drop_index(op.f('ix_admin_settings_id'), table_name='admin_settings')
    op.drop_table('admin_settings')
    
    # Drop vehicle_types table
    op.drop_index(op.f('ix_vehicle_types_name'), table_name='vehicle_types')
    op.drop_index(op.f('ix_vehicle_types_is_deleted'), table_name='vehicle_types')
    op.drop_index(op.f('ix_vehicle_types_id'), table_name='vehicle_types')
    op.drop_table('vehicle_types')

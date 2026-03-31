from telemetric_system.core.database.connection import get_engine
import sqlalchemy as sa

engine = get_engine()
with engine.connect() as conn:
    try:
        result = conn.execute(sa.text('SELECT version_num FROM alembic_version'))
        versions = [row[0] for row in result]
        if versions:
            print(f'Current migration version: {versions[0]}')
        else:
            print('No migration version found - database not stamped')
    except Exception as e:
        print(f'Error checking migration: {e}')
        print('alembic_version table might not exist')

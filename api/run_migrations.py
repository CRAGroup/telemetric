"""Run database migrations"""
import os
import sys
from pathlib import Path

# Add the api directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from alembic import command
from alembic.config import Config

def run_migrations():
    """Run all pending migrations"""
    # Get the directory containing this script
    base_dir = Path(__file__).parent
    
    # Create Alembic config
    alembic_cfg = Config(str(base_dir / "alembic.ini"))
    
    # Run upgrade to head
    print("Running migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()

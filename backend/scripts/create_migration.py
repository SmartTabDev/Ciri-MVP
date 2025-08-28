import os
import sys
from pathlib import Path
import argparse

# Add the project root directory to sys.path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from app.core.config import settings

def create_migration(message):
    """Create a new migration using Alembic."""
    # Get the absolute path to alembic.ini
    alembic_ini_path = os.path.join(project_root, "alembic.ini")
    
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    
    # Create the migration directory if it doesn't exist
    migrations_dir = Path(project_root) / "alembic" / "versions"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating migration with message: {message}")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    print("Migration created successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new database migration")
    parser.add_argument("message", help="Migration message")
    args = parser.parse_args()
    
    create_migration(args.message)

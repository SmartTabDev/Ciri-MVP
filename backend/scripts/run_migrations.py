import os
import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from app.core.config import settings

def run_migrations():
    """Run migrations using Alembic."""
    # Get the absolute path to alembic.ini
    alembic_ini_path = os.path.join(project_root, "alembic.ini")
    
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))
    
    # Create the migration directory if it doesn't exist
    migrations_dir = Path(project_root) / "alembic" / "versions"
    migrations_dir.mkdir(parents=True, exist_ok=True)
    
    print("Running database migrations...")
    command.upgrade(alembic_cfg, "head")
    print("Migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()

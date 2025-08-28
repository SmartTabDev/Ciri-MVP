import os
import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_db_connection():
    """Check the database connection."""
    try:
        print(f"Connecting to database: {settings.DATABASE_URL}")
        engine = create_engine(str(settings.DATABASE_URL))
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful!")
            
            # Check if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"Existing tables: {', '.join(tables)}")
            else:
                print("No tables found. You may need to run migrations.")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_db_connection()

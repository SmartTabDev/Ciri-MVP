#!/usr/bin/env python3
"""
Database migration script for Supabase
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def migrate_to_supabase():
    """Migrate database schema to Supabase"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.production')  # Use production environment
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in .env.production")
        print("Please update .env.production with your Supabase connection string")
        return False
    
    print(f"🔗 Connecting to Supabase: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to Supabase!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Check if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            existing_tables = [row[0] for row in result.fetchall()]
            print(f"📋 Existing tables: {', '.join(existing_tables) if existing_tables else 'No tables found'}")
            
            if 'alembic_version' in existing_tables:
                print("✅ Database already has Alembic version table")
                # Check current migration version
                result = connection.execute(text("SELECT version_num FROM alembic_version;"))
                current_version = result.fetchone()[0]
                print(f"📋 Current migration version: {current_version}")
            else:
                print("⚠️  No Alembic version table found. Running initial migration...")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your Supabase connection string in .env.production")
        print("2. Ensure your Supabase project is active")
        print("3. Check if your IP is allowed in Supabase settings")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def run_alembic_migrations():
    """Run Alembic migrations on Supabase"""
    print("\n🔄 Running Alembic migrations...")
    
    try:
        # Set environment to use production config
        os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL', '')
        
        # Run alembic upgrade
        import subprocess
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Migrations completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase Database Migration Tool")
    print("=" * 40)
    
    # Test connection first
    if not migrate_to_supabase():
        sys.exit(1)
    
    # Ask user if they want to run migrations
    response = input("\n❓ Do you want to run database migrations? (y/N): ")
    if response.lower() in ['y', 'yes']:
        if run_alembic_migrations():
            print("\n🎉 Database migration completed successfully!")
        else:
            print("\n❌ Database migration failed!")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping migrations. You can run them later with: alembic upgrade head")
    
    print("\n✅ Database setup complete!") 
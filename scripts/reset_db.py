#!/usr/bin/env python3
"""
Database reset script for LP Document Parser.
This script drops and recreates the database with fresh data.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def drop_database():
    """Drop the database if it exists."""
    try:
        from app.core.config import settings
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        
        # Terminate existing connections to the database
        cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{settings.db_name}' AND pid <> pg_backend_pid()
        """)
        
        # Drop the database
        cursor.execute(f"DROP DATABASE IF EXISTS {settings.db_name}")
        print(f"✅ Database '{settings.db_name}' dropped successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to drop database: {e}")
        return False


def create_database():
    """Create the database."""
    try:
        from app.core.config import settings
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {settings.db_name}")
        print(f"✅ Database '{settings.db_name}' created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False


def run_migrations():
    """Run database migrations."""
    try:
        print("🔄 Running database migrations...")
        
        # Apply migrations
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to apply migrations: {result.stderr}")
            return False
        
        print("✅ Migrations applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def create_default_admin():
    """Create default admin user."""
    try:
        from app.db.database import SessionLocal
        from app.models.user import User
        from app.core.security import get_password_hash
        
        db = SessionLocal()
        
        # Create default admin user
        hashed_password = get_password_hash("admin123")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Default admin user created:")
        print("   Username: admin")
        print("   Password: admin123")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False


def main():
    """Main reset function."""
    print("⚠️  WARNING: This will delete all data in the database!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        sys.exit(0)
    
    print("🔄 Resetting LP Document Parser Database...")
    print("=" * 50)
    
    # Step 1: Drop database
    print("\n1️⃣  Dropping existing database...")
    if not drop_database():
        sys.exit(1)
    
    # Step 2: Create database
    print("\n2️⃣  Creating fresh database...")
    if not create_database():
        sys.exit(1)
    
    # Step 3: Run migrations
    print("\n3️⃣  Running database migrations...")
    if not run_migrations():
        sys.exit(1)
    
    # Step 4: Create admin user
    print("\n4️⃣  Creating default admin user...")
    if not create_default_admin():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database reset completed successfully!")
    print("\n📋 You can now:")
    print("1. Run: python main.py")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Login with admin/admin123")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Database setup script for LP Document Parser.
This script helps you set up the database from scratch.
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_database_connection():
    """Check if database is accessible."""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_database():
    """Create the database if it doesn't exist."""
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
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {settings.db_name}")
            print(f"✅ Database '{settings.db_name}' created successfully!")
        else:
            print(f"ℹ️  Database '{settings.db_name}' already exists.")
        
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
        
        # Initialize Alembic if not already done
        if not Path("alembic/versions").exists():
            print("📁 Initializing Alembic...")
            result = subprocess.run(["alembic", "init", "alembic"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to initialize Alembic: {result.stderr}")
                return False
        
        # Create initial migration
        print("📝 Creating initial migration...")
        result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to create migration: {result.stderr}")
            return False
        
        # Apply migrations
        print("🚀 Applying migrations...")
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
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
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
            print("   ⚠️  Please change the password after first login!")
        else:
            print("ℹ️  Admin user already exists.")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False


def setup_directories():
    """Create necessary directories."""
    try:
        directories = ["uploads", "logs", "alembic/versions"]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up LP Document Parser Database...")
    print("=" * 50)
    
    # Step 1: Setup directories
    print("\n1️⃣  Setting up directories...")
    if not setup_directories():
        sys.exit(1)
    
    # Step 2: Create database
    print("\n2️⃣  Creating database...")
    if not create_database():
        print("💡 Make sure PostgreSQL is running and credentials are correct.")
        sys.exit(1)
    
    # Step 3: Check connection
    print("\n3️⃣  Testing database connection...")
    if not check_database_connection():
        print("💡 Check your database configuration in .env file.")
        sys.exit(1)
    
    # Step 4: Run migrations
    print("\n4️⃣  Running database migrations...")
    if not run_migrations():
        sys.exit(1)
    
    # Step 5: Create admin user
    print("\n5️⃣  Creating default admin user...")
    if not create_default_admin():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy env.example to .env and configure your settings")
    print("2. Run: python main.py")
    print("3. Visit: http://localhost:8000/docs")
    print("4. Login with admin/admin123 and change password")


if __name__ == "__main__":
    main()

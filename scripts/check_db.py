#!/usr/bin/env python3
"""
Database health check script for LP Document Parser.
This script checks database connectivity and provides status information.
"""
import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_database_connection():
    """Check if database is accessible."""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            if result:
                print("✅ Database connection: OK")
                return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False


def check_database_exists():
    """Check if the database exists."""
    try:
        from app.core.config import settings
        import psycopg2
        
        # Connect to PostgreSQL server (not to specific database)
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database='postgres'
        )
        
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.db_name}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{settings.db_name}' exists")
        else:
            print(f"❌ Database '{settings.db_name}' does not exist")
        
        cursor.close()
        conn.close()
        return exists is not None
        
    except Exception as e:
        print(f"❌ Failed to check database existence: {e}")
        return False


def check_tables():
    """Check if required tables exist."""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Get list of tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            required_tables = [
                'users', 'documents', 'capital_call_details', 
                'distribution_details', 'processing_logs', 'document_templates'
            ]
            
            print("\n📊 Database Tables:")
            for table in required_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} (missing)")
            
            return len(tables) > 0
        
    except Exception as e:
        print(f"❌ Failed to check tables: {e}")
        return False


def check_migration_status():
    """Check Alembic migration status."""
    try:
        import subprocess
        
        print("\n🔄 Migration Status:")
        result = subprocess.run(["alembic", "current"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  Current: {result.stdout.strip()}")
        else:
            print(f"  ❌ Failed to check migration status: {result.stderr}")
            return False
        
        # Check for pending migrations
        result = subprocess.run(["alembic", "heads"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"  Head: {result.stdout.strip()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check migration status: {e}")
        return False


def get_database_info():
    """Get database information."""
    try:
        from app.db.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Database size
            result = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            db_size = result.fetchone()[0]
            
            # Connection count
            result = conn.execute(text("SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"))
            conn_count = result.fetchone()[0]
            
            print(f"\n📈 Database Info:")
            print(f"  Size: {db_size}")
            print(f"  Active Connections: {conn_count}")
            
            return True
        
    except Exception as e:
        print(f"❌ Failed to get database info: {e}")
        return False


def check_admin_user():
    """Check if admin user exists."""
    try:
        from app.db.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if admin_user:
            print("✅ Admin user exists")
            print(f"  Username: {admin_user.username}")
            print(f"  Email: {admin_user.email}")
            print(f"  Active: {admin_user.is_active}")
            print(f"  Admin: {admin_user.is_admin}")
        else:
            print("❌ Admin user does not exist")
        
        db.close()
        return admin_user is not None
        
    except Exception as e:
        print(f"❌ Failed to check admin user: {e}")
        return False


def main():
    """Main health check function."""
    print("🏥 LP Document Parser - Database Health Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check database connection
    print("\n1️⃣  Database Connection:")
    db_connected = check_database_connection()
    
    if not db_connected:
        print("\n💡 Troubleshooting tips:")
        print("1. Check if PostgreSQL is running")
        print("2. Verify database credentials in .env file")
        print("3. Ensure database exists")
        print("4. Check network connectivity")
        return
    
    # Check database existence
    print("\n2️⃣  Database Existence:")
    db_exists = check_database_exists()
    
    # Check tables
    print("\n3️⃣  Database Tables:")
    tables_ok = check_tables()
    
    # Check migration status
    print("\n4️⃣  Migration Status:")
    migration_ok = check_migration_status()
    
    # Get database info
    print("\n5️⃣  Database Information:")
    info_ok = get_database_info()
    
    # Check admin user
    print("\n6️⃣  Admin User:")
    admin_ok = check_admin_user()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Summary:")
    
    if all([db_connected, db_exists, tables_ok, migration_ok]):
        print("✅ Database is healthy and ready to use!")
    else:
        print("⚠️  Database has some issues that need attention.")
        
        if not db_exists:
            print("💡 Run: python scripts/setup_db.py")
        elif not tables_ok:
            print("💡 Run: alembic upgrade head")
        elif not migration_ok:
            print("💡 Check migration files and run: alembic upgrade head")
    
    if not admin_ok:
        print("💡 Create admin user: python scripts/create_user.py admin admin@example.com admin123 --admin")


if __name__ == "__main__":
    main()

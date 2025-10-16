#!/usr/bin/env python3
"""
Script to initialize the database with tables and default data.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import init_db
from app.core.security import get_password_hash
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.database import SessionLocal


def create_default_admin():
    """Create default admin user if it doesn't exist."""
    db: Session = SessionLocal()
    try:
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
            print("Default admin user created: username='admin', password='admin123'")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    
    print("Creating default admin user...")
    create_default_admin()
    print("Database setup complete!")

#!/usr/bin/env python3
"""
Script to create a new user for the LP Document Parser.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_user(username: str, email: str, password: str, is_admin: bool = False):
    """Create a new user."""
    db: Session = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists.")
            return False
        
        # Create new user
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"User '{username}' created successfully with ID: {db_user.id}")
        return True
        
    except Exception as e:
        print(f"Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_user.py <username> <email> <password> [--admin]")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    is_admin = "--admin" in sys.argv
    
    success = create_user(username, email, password, is_admin)
    sys.exit(0 if success else 1)

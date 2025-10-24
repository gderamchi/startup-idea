#!/usr/bin/env python3
"""
Initialize database with tables
"""
import sys
sys.path.insert(0, 'backend')

from app.db.session import engine, Base
from app.models import User, Project, Feedback, Revision, ActionItem, Notification

def init_db():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)

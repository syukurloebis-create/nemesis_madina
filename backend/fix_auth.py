#!/usr/bin/env python3
"""
Fix Authentication - Reset password admin dan buat user test
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import uuid
from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool

try:
    from backend.config import settings
except ImportError:
    from config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, poolclass=NullPool)

def hash_password(password: str) -> str:
    """Hash password dengan SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def fix_auth():
    print("=" * 60)
    print("🔧 FIXING AUTHENTICATION")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Reset admin password
        admin_password = hash_password("admin123")
        conn.execute(
            text("""
                UPDATE users 
                SET password_hash = :password_hash
                WHERE username = 'admin'
            """),
            {"password_hash": admin_password}
        )
        conn.commit()
        print("✅ Admin password reset to: admin123")
        
        # 2. Create test investigator if not exists
        investigator_exists = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE username = 'investigator'")
        ).scalar()
        
        if investigator_exists == 0:
            investigator_password = hash_password("invest123")
            conn.execute(
                text("""
                    INSERT INTO users (id, username, email, full_name, password_hash, role, is_active)
                    VALUES (
                        :id, 
                        :username, 
                        :email, 
                        :full_name, 
                        :password_hash, 
                        :role, 
                        :is_active
                    )
                """),
                {
                    "id": str(uuid.uuid4()),
                    "username": "investigator",
                    "email": "invest@nemesis.local",
                    "full_name": "Test Investigator",
                    "password_hash": investigator_password,
                    "role": "investigator",
                    "is_active": "true"
                }
            )
            conn.commit()
            print("✅ Created investigator user (password: invest123)")
        
        # 3. Create test reviewer if not exists
        reviewer_exists = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE username = 'reviewer'")
        ).scalar()
        
        if reviewer_exists == 0:
            reviewer_password = hash_password("review123")
            conn.execute(
                text("""
                    INSERT INTO users (id, username, email, full_name, password_hash, role, is_active)
                    VALUES (
                        :id, 
                        :username, 
                        :email, 
                        :full_name, 
                        :password_hash, 
                        :role, 
                        :is_active
                    )
                """),
                {
                    "id": str(uuid.uuid4()),
                    "username": "reviewer",
                    "email": "review@nemesis.local",
                    "full_name": "Test Reviewer",
                    "password_hash": reviewer_password,
                    "role": "reviewer",
                    "is_active": "true"
                }
            )
            conn.commit()
            print("✅ Created reviewer user (password: review123)")
        
        # 4. List all users
        users = conn.execute(
            text("""
                SELECT username, email, role, is_active 
                FROM users 
                ORDER BY username
            """)
        ).fetchall()
        
        print("\n📊 Users:")
        for user in users:
            print(f"  - {user[0]} ({user[1]}) role: {user[2]} active: {user[3]}")

if __name__ == "__main__":
    fix_auth()
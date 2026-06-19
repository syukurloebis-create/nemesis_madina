#!/usr/bin/env python3
"""
Database Migration Runner
Run: python scripts/migrate.py
"""

import sqlite3
import os
from pathlib import Path

MIGRATIONS_DIR = Path(__file__).parent.parent / "backend" / "migrations"
DB_PATH = Path(__file__).parent.parent / "nemesis.db"

def get_applied_migrations(conn):
    """Get list of already applied migrations"""
    try:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        if not cursor.fetchone():
            return set()
        cursor = conn.execute("SELECT migration_name FROM migrations ORDER BY applied_at")
        return {row[0] for row in cursor.fetchall()}
    except:
        return set()

def apply_migration(conn, migration_file):
    """Apply a single migration"""
    print(f"Applying: {migration_file}")
    with open(MIGRATIONS_DIR / migration_file, 'r') as f:
        sql = f.read()
    
    try:
        conn.executescript(sql)
        conn.execute("INSERT INTO migrations (migration_name) VALUES (?)", (migration_file,))
        conn.commit()
        print(f"✅ Applied: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Failed: {migration_file} - {e}")
        return False

def main():
    print("=" * 50)
    print("NEMESIS Database Migration")
    print("=" * 50)
    
    # Ensure migrations table exists
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT UNIQUE,
            applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    applied = get_applied_migrations(conn)
    
    # Get all migration files
    migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith('.sql')])
    
    pending = [f for f in migration_files if f not in applied]
    
    if not pending:
        print("✅ No pending migrations")
        return
    
    print(f"Found {len(pending)} pending migrations")
    
    for migration in pending:
        if not apply_migration(conn, migration):
            print("❌ Migration failed, rolling back...")
            conn.rollback()
            return
    
    print("=" * 50)
    print("✅ All migrations applied successfully")
    print("=" * 50)

if __name__ == "__main__":
    main()

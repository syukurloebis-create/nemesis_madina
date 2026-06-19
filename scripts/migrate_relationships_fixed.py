#!/usr/bin/env python3
"""
Fix migration untuk relationships - mapping SQLite ke PostgreSQL
"""

import sqlite3
import psycopg2
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_DSN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def fix_relationships():
    """Migrasi relationships dengan mapping yang benar"""
    print("\n📊 Fixing relationships migration...")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Cek struktur SQLite
    sqlite_cursor.execute("PRAGMA table_info(relationships)")
    columns = [row[1] for row in sqlite_cursor.fetchall()]
    print(f"   SQLite columns: {columns}")
    
    # Query sesuai kolom SQLite yang ada
    sqlite_cursor.execute("""
        SELECT id, endorser_id, target_id, relationship_type, weight, created_at
        FROM relationships
    """)
    rows = sqlite_cursor.fetchall()
    total = len(rows)
    print(f"   Found {total} relationships in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    pg_conn = psycopg2.connect(PG_DSN)
    pg_cursor = pg_conn.cursor()
    
    # Cek data existing
    pg_cursor.execute("SELECT COUNT(*) FROM relationships")
    existing = pg_cursor.fetchone()[0]
    print(f"   Existing records in PostgreSQL: {existing}")
    
    inserted = 0
    for row in rows:
        try:
            # Mapping: SQLite → PostgreSQL
            # endorser_id → source_id
            # target_id → target_id  
            # relationship_type → relationship_type
            source_id = row['endorser_id']
            target_id = row['target_id']
            relationship_type = row['relationship_type']
            weight = row['weight']
            
            created_at = row['created_at']
            if isinstance(created_at, (int, float)):
                created_at = datetime.fromtimestamp(created_at)
            
            pg_cursor.execute("""
                INSERT INTO relationships (
                    source_id, target_id, relationship_type, weight, created_at, endorser_id
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (source_id, target_id, relationship_type, weight, created_at, source_id))
            inserted += 1
            
            if inserted % 100 == 0:
                print(f"   Progress: {inserted}/{total}")
                pg_conn.commit()
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} relationships")
    return inserted

if __name__ == "__main__":
    fix_relationships()

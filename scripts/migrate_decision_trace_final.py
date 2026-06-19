#!/usr/bin/env python3
"""
Migrasi decision_trace - biarkan PostgreSQL generate UUID baru
"""

import sqlite3
import psycopg2
import json
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_DSN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def migrate_decision_trace():
    """Migrasi decision_trace tanpa trace_id (biar PG yang generate)"""
    print("\n📊 Migrating decision_trace...")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Ambil data dari SQLite (tanpa trace_id)
    sqlite_cursor.execute("""
        SELECT entity_id, entity_type, decision_type, score, 
               reasons, evidence_ids, lineage_ids, created_at
        FROM decision_trace
    """)
    rows = sqlite_cursor.fetchall()
    total = len(rows)
    print(f"   Found {total} decision traces in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    pg_conn = psycopg2.connect(PG_DSN)
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            # Biarkan PostgreSQL generate trace_id sendiri (DEFAULT gen_random_uuid())
            pg_cursor.execute("""
                INSERT INTO decision_trace (
                    entity_id, entity_type, decision_type, score,
                    reasons, evidence_ids, lineage_ids, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                row['entity_id'],
                row['entity_type'],
                row['decision_type'],
                row['score'],
                row['reasons'],
                row['evidence_ids'],
                row['lineage_ids'],
                row['created_at']
            ))
            inserted += 1
            
            if inserted % 10 == 0:
                print(f"   Progress: {inserted}/{total}")
                pg_conn.commit()
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} decision traces")
    return inserted

if __name__ == "__main__":
    migrate_decision_trace()

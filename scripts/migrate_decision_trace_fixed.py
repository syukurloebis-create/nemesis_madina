#!/usr/bin/env python3
"""
Fix migration untuk decision_trace - sesuai schema PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_DSN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def fix_decision_trace():
    """Migrasi decision_trace dengan field yang benar"""
    print("\n📊 Fixing decision_trace migration...")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Cek struktur SQLite
    sqlite_cursor.execute("PRAGMA table_info(decision_trace)")
    columns = [row[1] for row in sqlite_cursor.fetchall()]
    print(f"   SQLite columns: {columns}")
    
    # Query sesuai kolom yang ada
    sqlite_cursor.execute("""
        SELECT trace_id, entity_id, entity_type, decision_type, score,
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
            pg_cursor.execute("""
                INSERT INTO decision_trace (
                    trace_id, entity_id, entity_type, decision_type, score,
                    reasons, evidence_ids, lineage_ids, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trace_id) DO NOTHING
            """, (
                row['trace_id'],
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
    fix_decision_trace()

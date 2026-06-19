#!/usr/bin/env python3
"""
Migrasi investigation_case - sesuai schema PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime
import uuid

SQLITE_PATH = "nemesis.db"
PG_DSN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def migrate_investigation_case():
    """Migrasi investigation_case"""
    print("\n📊 Migrating investigation_case...")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Cek apakah ada data
    sqlite_cursor.execute("SELECT COUNT(*) FROM investigation_case")
    total = sqlite_cursor.fetchone()[0]
    print(f"   Found {total} investigation cases in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    # Ambil data dari SQLite
    sqlite_cursor.execute("""
        SELECT case_id, case_number, title, description, status, priority,
               assigned_to, evidence_ids, findings, timeline, 
               created_at, updated_at, closed_at, metadata, risk_level
        FROM investigation_case
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = psycopg2.connect(PG_DSN)
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            # Convert jika perlu
            case_id = row['case_id']
            # Jika case_id bukan UUID format, generate baru
            try:
                uuid.UUID(str(case_id))
            except:
                case_id = str(uuid.uuid4())
            
            pg_cursor.execute("""
                INSERT INTO investigation_case (
                    case_id, case_number, title, description, status, priority,
                    assigned_to, evidence_ids, findings, timeline,
                    created_at, updated_at, closed_at, metadata, risk_level
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (case_id) DO NOTHING
            """, (
                case_id,
                row['case_number'],
                row['title'],
                row['description'],
                row['status'],
                row['priority'],
                row['assigned_to'],
                row['evidence_ids'],
                row['findings'],
                row['timeline'],
                row['created_at'],
                row['updated_at'],
                row['closed_at'],
                row['metadata'],
                row['risk_level']
            ))
            inserted += 1
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} investigation cases")
    return inserted

def migrate_finding():
    """Migrasi finding"""
    print("\n📊 Migrating finding...")
    
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    sqlite_cursor.execute("SELECT COUNT(*) FROM finding")
    total = sqlite_cursor.fetchone()[0]
    print(f"   Found {total} findings in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT finding_id, case_id, finding_number, title, description,
               severity, status, evidence_ids, trace_ids,
               recommendation, response, created_at, updated_at,
               resolved_at, resolved_by
        FROM finding
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = psycopg2.connect(PG_DSN)
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO finding (
                    finding_id, case_id, finding_number, title, description,
                    severity, status, evidence_ids, trace_ids,
                    recommendation, response, created_at, updated_at,
                    resolved_at, resolved_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (finding_id) DO NOTHING
            """, (
                row['finding_id'],
                row['case_id'],
                row['finding_number'],
                row['title'],
                row['description'],
                row['severity'],
                row['status'],
                row['evidence_ids'],
                row['trace_ids'],
                row['recommendation'],
                row['response'],
                row['created_at'],
                row['updated_at'],
                row['resolved_at'],
                row['resolved_by']
            ))
            inserted += 1
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} findings")
    return inserted

if __name__ == "__main__":
    migrate_investigation_case()
    migrate_finding()

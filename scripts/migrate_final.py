#!/usr/bin/env python3
"""
Migrasi data dari SQLite ke PostgreSQL - dengan struktur yang tepat
"""

import sqlite3
import psycopg2
import json
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_CONN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def get_sqlite_connection():
    return sqlite3.connect(SQLITE_PATH)

def get_pg_connection():
    return psycopg2.connect(PG_CONN)

def migrate_anomalies():
    """Migrasi anomalies (48,190 rows)"""
    print("\n  Migrating anomalies...")
    
    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) FROM anomalies")
    total = sqlite_cursor.fetchone()[0]
    print(f"    Found {total} rows in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT id, entity_id, anomaly_type, severity, details, 
               detected_at, resolved, metadata, confidence, 
               requires_review, evidence
        FROM anomalies
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO anomalies (
                    id, entity_id, anomaly_type, severity, details,
                    detected_at, resolved, metadata, confidence,
                    requires_review, evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, row)
            inserted += 1
            if inserted % 5000 == 0:
                print(f"      Progress: {inserted}/{total}")
                pg_conn.commit()
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"    ✅ Migrated {inserted}/{total} anomalies")
    return inserted

def migrate_entities():
    """Migrasi entities (106 rows)"""
    print("\n  Migrating entities...")
    
    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) FROM entities")
    total = sqlite_cursor.fetchone()[0]
    print(f"    Found {total} rows in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT entity_id, entity_type, trust_score, last_update, created_at
        FROM entities
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            entity_id, entity_type, trust_score, last_update, created_at = row
            
            # Convert timestamp if needed
            if isinstance(created_at, (int, float)):
                created_at = datetime.fromtimestamp(created_at)
            if isinstance(last_update, (int, float)):
                last_update = datetime.fromtimestamp(last_update)
            
            pg_cursor.execute("""
                INSERT INTO entities (
                    entity_id, entity_type, trust_score, last_update, created_at
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (entity_id) DO UPDATE SET
                    trust_score = EXCLUDED.trust_score,
                    last_update = EXCLUDED.last_update
            """, (entity_id, entity_type, trust_score, last_update, created_at))
            inserted += 1
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"    ✅ Migrated {inserted}/{total} entities")
    return inserted

def migrate_decision_trace():
    """Migrasi decision_trace (2 rows)"""
    print("\n  Migrating decision_trace...")
    
    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) FROM decision_trace")
    total = sqlite_cursor.fetchone()[0]
    print(f"    Found {total} rows in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT trace_id, entity_id, entity_type, decision_type, score,
               confidence, reasons, evidence_ids, lineage_ids,
               feature_importance, model_version, created_by, created_at, metadata
        FROM decision_trace
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO decision_trace (
                    trace_id, entity_id, entity_type, decision_type, score,
                    confidence, reasons, evidence_ids, lineage_ids,
                    feature_importance, model_version, created_by, created_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trace_id) DO NOTHING
            """, row)
            inserted += 1
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"    ✅ Migrated {inserted}/{total} decision traces")
    return inserted

def migrate_investigation_case():
    """Migrasi investigation_case (1 row)"""
    print("\n  Migrating investigation_case...")
    
    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) FROM investigation_case")
    total = sqlite_cursor.fetchone()[0]
    print(f"    Found {total} rows in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT case_id, case_number, title, description, status, priority,
               risk_level, assigned_to, assigned_by, assigned_at,
               evidence_ids, trace_ids, findings, timeline,
               created_at, updated_at, closed_at, closed_by, closure_reason, metadata
        FROM investigation_case
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO investigation_case (
                    case_id, case_number, title, description, status, priority,
                    risk_level, assigned_to, assigned_by, assigned_at,
                    evidence_ids, trace_ids, findings, timeline,
                    created_at, updated_at, closed_at, closed_by, closure_reason, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (case_id) DO NOTHING
            """, row)
            inserted += 1
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"    ✅ Migrated {inserted}/{total} investigation cases")
    return inserted

def migrate_relationships():
    """Migrasi relationships"""
    print("\n  Migrating relationships...")
    
    sqlite_conn = get_sqlite_connection()
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT COUNT(*) FROM relationships")
    total = sqlite_cursor.fetchone()[0]
    print(f"    Found {total} rows in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    sqlite_cursor.execute("""
        SELECT id, endorser_id, target_id, relationship_type, weight, created_at
        FROM relationships
    """)
    rows = sqlite_cursor.fetchall()
    
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO relationships (
                    id, endorser_id, target_id, relationship_type, weight, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, row)
            inserted += 1
        except Exception as e:
            print(f"      Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"    ✅ Migrated {inserted}/{total} relationships")
    return inserted

def main():
    print("=" * 60)
    print("MIGRASI SQLITE -> POSTGRESQL")
    print("=" * 60)
    
    total = 0
    total += migrate_anomalies()
    total += migrate_entities()
    total += migrate_decision_trace()
    total += migrate_investigation_case()
    total += migrate_relationships()
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL MIGRATED: {total} rows")
    print("=" * 60)
    
    # Verify
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()
    
    print("\n📊 Final counts in PostgreSQL:")
    for table in ["anomalies", "entities", "decision_trace", "investigation_case", "relationships"]:
        pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = pg_cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
    
    pg_cursor.close()
    pg_conn.close()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fixed Migration - SQLite to PostgreSQL
Hanya field yang ada di schema PostgreSQL
"""

import sqlite3
import psycopg2
import json
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_DSN = "dbname=madina user=nemesis password=nemesis123 host=localhost port=5432"

def get_pg_conn():
    return psycopg2.connect(PG_DSN)

def get_sqlite_conn():
    return sqlite3.connect(SQLITE_PATH)

def migrate_anomalies():
    """Migrasi anomalies - 48,190 rows"""
    print("\n📊 Migrating anomalies...")
    
    sqlite_conn = get_sqlite_conn()
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM anomalies")
    total = cursor.fetchone()[0]
    print(f"   Found {total} anomalies in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    cursor.execute("""
        SELECT id, entity_id, anomaly_type, severity, details, 
               detected_at, resolved, metadata, confidence, 
               requires_review, evidence
        FROM anomalies
    """)
    rows = cursor.fetchall()
    
    pg_conn = get_pg_conn()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            detected_at = row[5]
            if isinstance(detected_at, (int, float)):
                detected_at = datetime.fromtimestamp(detected_at)
            
            pg_cursor.execute("""
                INSERT INTO anomalies (
                    id, entity_id, anomaly_type, severity, details,
                    detected_at, resolved, metadata, confidence,
                    requires_review, evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                row[0], row[1], row[2], row[3], row[4],
                detected_at, row[6], row[7], row[8], row[9], row[10]
            ))
            inserted += 1
            
            if inserted % 5000 == 0:
                print(f"   Progress: {inserted}/{total}")
                pg_conn.commit()
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} anomalies")
    return inserted

def migrate_entities():
    """Migrasi entities"""
    print("\n📊 Migrating entities...")
    
    sqlite_conn = get_sqlite_conn()
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM entities")
    total = cursor.fetchone()[0]
    print(f"   Found {total} entities in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    cursor.execute("SELECT entity_id, entity_type, trust_score, last_update, created_at FROM entities")
    rows = cursor.fetchall()
    
    pg_conn = get_pg_conn()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            created_at = row[4]
            if isinstance(created_at, (int, float)):
                created_at = datetime.fromtimestamp(created_at)
            
            last_update = row[3]
            if isinstance(last_update, (int, float)):
                last_update = datetime.fromtimestamp(last_update)
            
            pg_cursor.execute("""
                INSERT INTO entities (
                    entity_id, entity_type, trust_score, last_update, created_at, name
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (entity_id) DO UPDATE SET
                    trust_score = EXCLUDED.trust_score,
                    last_update = EXCLUDED.last_update
            """, (row[0], row[1], row[2], last_update, created_at, row[0]))
            inserted += 1
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} entities")
    return inserted

def migrate_decision_traces():
    """Migrasi decision_trace - tanpa field yang tidak ada"""
    print("\n📊 Migrating decision_trace...")
    
    sqlite_conn = get_sqlite_conn()
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM decision_trace")
    total = cursor.fetchone()[0]
    print(f"   Found {total} decision traces in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    # Hanya field yang ada di schema PostgreSQL
    cursor.execute("""
        SELECT trace_id, entity_id, entity_type, decision_type, score,
               reasons, evidence_ids, lineage_ids, created_at, metadata
        FROM decision_trace
    """)
    rows = cursor.fetchall()
    
    pg_conn = get_pg_conn()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO decision_trace (
                    trace_id, entity_id, entity_type, decision_type, score,
                    reasons, evidence_ids, lineage_ids, created_at, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (trace_id) DO NOTHING
            """, row)
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

def migrate_relationships():
    """Migrasi relationships"""
    print("\n📊 Migrating relationships...")
    
    sqlite_conn = get_sqlite_conn()
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM relationships")
    total = cursor.fetchone()[0]
    print(f"   Found {total} relationships in SQLite")
    
    if total == 0:
        sqlite_conn.close()
        return 0
    
    cursor.execute("SELECT id, endorser_id, target_id, relationship_type, weight, created_at FROM relationships")
    rows = cursor.fetchall()
    
    pg_conn = get_pg_conn()
    pg_cursor = pg_conn.cursor()
    
    inserted = 0
    for row in rows:
        try:
            created_at = row[5]
            if isinstance(created_at, (int, float)):
                created_at = datetime.fromtimestamp(created_at)
            
            pg_cursor.execute("""
                INSERT INTO relationships (
                    id, source_id, target_id, edge_type, weight, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (row[0], row[1], row[2], row[3], row[4], created_at))
            inserted += 1
        except Exception as e:
            print(f"   Error: {e}")
            continue
    
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_conn.close()
    
    print(f"   ✅ Migrated {inserted}/{total} relationships")
    return inserted

def main():
    print("=" * 60)
    print("FIXED MIGRATION - SQLITE TO POSTGRESQL")
    print("=" * 60)
    
    total = 0
    total += migrate_anomalies()
    total += migrate_entities()
    total += migrate_decision_traces()
    total += migrate_relationships()
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL MIGRATED: {total} rows")
    print("=" * 60)

if __name__ == "__main__":
    main()

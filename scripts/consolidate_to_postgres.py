#!/usr/bin/env python3
"""
Konsolidasi data dari SQLite ke PostgreSQL
Password: nemesis123
"""

import sqlite3
import asyncpg
import asyncio
import json
from datetime import datetime

SQLITE_PATH = "nemesis.db"
PG_DSN = "postgresql://nemesis:nemesis123@localhost:5432/madina"

async def migrate_table(pg_conn, sqlite_conn, table_name, id_column=None):
    """Migrate single table"""
    print(f"\n  Migrating {table_name}...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"    No data in {table_name}")
        return 0
    
    column_names = [desc[0] for desc in cursor.description]
    placeholders = ','.join([f"${i+1}" for i in range(len(column_names))])
    columns_str = ','.join(column_names)
    
    inserted = 0
    for row in rows:
        try:
            # Convert row to list and handle special types
            row_list = list(row)
            for i, val in enumerate(row_list):
                if isinstance(val, bytes):
                    row_list[i] = val.decode('utf-8')
                elif isinstance(val, (dict, list)):
                    row_list[i] = json.dumps(val)
            
            if id_column:
                query = f"""
                    INSERT INTO {table_name} ({columns_str}) 
                    VALUES ({placeholders})
                    ON CONFLICT ({id_column}) DO NOTHING
                """
            else:
                query = f"""
                    INSERT INTO {table_name} ({columns_str}) 
                    VALUES ({placeholders})
                """
            await pg_conn.execute(query, *row_list)
            inserted += 1
            
            if inserted % 5000 == 0:
                print(f"    Progress: {inserted} rows migrated")
                
        except Exception as e:
            print(f"    Error: {e}")
            continue
    
    print(f"    ✅ Migrated {inserted} rows")
    return inserted

async def main():
    print("=" * 60)
    print("KONSOLIDASI DATA SQLITE -> POSTGRESQL")
    print("=" * 60)
    
    # Koneksi ke SQLite
    print(f"\n📂 Connecting to SQLite: {SQLITE_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Koneksi ke PostgreSQL
    print(f"🐘 Connecting to PostgreSQL: {PG_DSN.split('@')[0]}...")
    pg_conn = await asyncpg.connect(PG_DSN)
    print("✅ Connected to PostgreSQL")
    
    # Daftar tabel yang akan dimigrasi
    tables = [
        ("anomalies", "id"),
        ("entities", "entity_id"),
        ("decision_trace", "trace_id"),
        ("investigation_case", "case_id"),
        ("outbox_events", "id"),
        ("trust_audit_log", "id"),
        ("relationships", "id"),
    ]
    
    total = 0
    for table_name, id_col in tables:
        count = await migrate_table(pg_conn, sqlite_conn, table_name, id_col)
        total += count
    
    print("\n" + "=" * 60)
    print(f"✅ KONSOLIDASI SELESAI: {total} rows migrated")
    print("=" * 60)
    
    # Verifikasi
    print("\n📊 Final counts in PostgreSQL:")
    for table_name, _ in tables:
        try:
            count = await pg_conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
            print(f"  {table_name}: {count} rows")
        except Exception as e:
            print(f"  {table_name}: error - {e}")
    
    await pg_conn.close()
    sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(main())

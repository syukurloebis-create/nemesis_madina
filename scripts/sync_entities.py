# scripts/sync_entities.py
import asyncpg
import sqlite3
import os
import asyncio

async def sync_entities():
    """Sync entities from PostgreSQL event_lineage to SQLite entities table"""
    
    # Connect to PostgreSQL
    pg_conn = await asyncpg.connect(
        os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    )
    
    # Get unique OPDs from event_lineage
    rows = await pg_conn.fetch("""
        SELECT DISTINCT 
            payload->>'opd' as entity_id,
            'opd' as entity_type,
            AVG(CAST(payload->>'pagu' AS FLOAT)) / 1000000000 as trust_score
        FROM event_lineage
        WHERE payload->>'opd' IS NOT NULL AND payload->>'opd' != ''
        GROUP BY payload->>'opd'
        UNION
        SELECT DISTINCT 
            aggregate_id as entity_id,
            'procurement' as entity_type,
            0.5 as trust_score
        FROM event_lineage
        WHERE aggregate_id LIKE 'rup-%'
        LIMIT 100
    """)
    
    await pg_conn.close()
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect("nemesis.db")
    cursor = sqlite_conn.cursor()
    
    # Clear old entities (optional)
    cursor.execute("DELETE FROM entities WHERE entity_type IN ('opd', 'procurement')")
    
    # Insert new entities
    for row in rows:
        cursor.execute("""
            INSERT OR REPLACE INTO entities (entity_id, entity_type, trust_score, created_at)
            VALUES (?, ?, ?, strftime('%s', 'now'))
        """, (row['entity_id'], row['entity_type'], row['trust_score']))
    
    sqlite_conn.commit()
    sqlite_conn.close()
    
    print(f"✅ Synced {len(rows)} entities to SQLite")

if __name__ == "__main__":
    asyncio.run(sync_entities())

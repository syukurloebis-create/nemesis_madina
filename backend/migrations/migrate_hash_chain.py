# backend/migrations/migrate_hash_chain.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Add indexes untuk hash chain
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_event_lineage_hash ON event_lineage(event_hash);
        CREATE INDEX IF NOT EXISTS idx_event_lineage_prev_hash ON event_lineage(previous_hash);
    """)
    print("✅ Hash chain indexes created")
    
    await conn.close()
    print("✅ Hash chain migration completed")

if __name__ == "__main__":
    asyncio.run(run_migration())

# backend/migrations/migrate_phase54.py
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def run_migration():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Create entity_trust_summary table (read model)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS entity_trust_summary (
            entity_id TEXT PRIMARY KEY,
            trust_score REAL DEFAULT 0.5,
            last_update TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    print("✅ Table entity_trust_summary created")
    
    # Add indexes
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_trust_summary_score ON entity_trust_summary(trust_score)
    """)
    print("✅ Indexes created")
    
    await conn.close()
    print("✅ Phase 5.4 migration completed")

if __name__ == "__main__":
    asyncio.run(run_migration())

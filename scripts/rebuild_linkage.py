#!/usr/bin/env python
# scripts/rebuild_linkage.py
import asyncio
import asyncpg
import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.security.hashing import build_event_hash

async def rebuild_linkage():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Ambil semua aggregate yang sudah memiliki rebuilt_hash
    rows = await conn.fetch("""
        SELECT DISTINCT aggregate_id
        FROM event_lineage
        WHERE rebuilt_hash IS NOT NULL
        ORDER BY aggregate_id
    """)
    
    print(f"🔄 Rebuilding linkage for {len(rows)} aggregates...")
    
    for agg in rows:
        agg_id = agg['aggregate_id']
        events = await conn.fetch("""
            SELECT event_id, sequence_num, event_type, payload, rebuilt_hash
            FROM event_lineage
            WHERE aggregate_id = $1 AND rebuilt_hash IS NOT NULL
            ORDER BY sequence_num ASC
        """, agg_id)
        
        prev_hash = None
        for ev in events:
            # Hitung previous_hash untuk rebuilt chain
            await conn.execute("""
                UPDATE event_lineage
                SET rebuilt_previous_hash = $1
                WHERE event_id = $2
            """, prev_hash, ev['event_id'])
            
            prev_hash = ev['rebuilt_hash']
        
        print(f"   ✅ Linked {len(events)} events for {agg_id}")
    
    await conn.close()
    print("✅ Linkage rebuild complete")

if __name__ == "__main__":
    asyncio.run(rebuild_linkage())

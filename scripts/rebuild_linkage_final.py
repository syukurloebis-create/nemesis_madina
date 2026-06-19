#!/usr/bin/env python
# scripts/rebuild_linkage_final.py
import asyncio
import asyncpg
import os
import sys

async def rebuild_linkage():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Ambil semua aggregate yang memiliki rebuilt_hash
    aggregates = await conn.fetch("""
        SELECT DISTINCT aggregate_id
        FROM event_lineage
        WHERE rebuilt_hash IS NOT NULL
        ORDER BY aggregate_id
    """)
    
    print(f"🔄 Rebuilding linkage for {len(aggregates)} aggregates...")
    
    total_updated = 0
    for agg in aggregates:
        agg_id = agg['aggregate_id']
        
        # Ambil semua event dalam aggregate, urutkan berdasarkan sequence
        events = await conn.fetch("""
            SELECT event_id, sequence_num, rebuilt_hash
            FROM event_lineage
            WHERE aggregate_id = $1 AND rebuilt_hash IS NOT NULL
            ORDER BY sequence_num ASC
        """, agg_id)
        
        prev_hash = None
        for ev in events:
            # Update rebuilt_previous_hash dengan hash dari event sebelumnya
            await conn.execute("""
                UPDATE event_lineage
                SET rebuilt_previous_hash = $1
                WHERE event_id = $2
            """, prev_hash, ev['event_id'])
            
            prev_hash = ev['rebuilt_hash']
            total_updated += 1
        
        print(f"   ✅ {agg_id}: {len(events)} events linked")
    
    await conn.close()
    print(f"\n✅ COMPLETE: {total_updated} events updated with rebuilt_previous_hash")

if __name__ == "__main__":
    asyncio.run(rebuild_linkage())

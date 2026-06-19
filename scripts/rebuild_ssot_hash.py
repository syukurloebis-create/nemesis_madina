#!/usr/bin/env python3
import asyncio
import asyncpg
import sys
import os
from datetime import datetime

# Tambahkan path project ke sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.security.hashing import build_event_hash

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/madina"

async def rebuild_all_hash_chains():
    conn = await asyncpg.connect(DATABASE_URL)
    print("✅ Connected to database")
    
    # Ambil semua aggregate
    aggregates = await conn.fetch("""
        SELECT DISTINCT aggregate_id
        FROM event_lineage
        ORDER BY aggregate_id
    """)
    
    print(f"📊 Found {len(aggregates)} aggregates")
    
    total_rebuilt = 0
    for agg in aggregates:
        agg_id = agg["aggregate_id"]
        events = await conn.fetch("""
            SELECT id, sequence_num, event_type, payload
            FROM event_lineage
            WHERE aggregate_id = $1
            ORDER BY sequence_num
        """, agg_id)
        
        previous_hash = ""
        for event in events:
            # Hitung hash baru dengan SSOT
            new_hash = build_event_hash(
                aggregate_id=agg_id,
                sequence_num=event["sequence_num"],
                event_type=event["event_type"],
                payload=event["payload"],
                previous_hash=previous_hash
            )
            
            # Update database
            await conn.execute("""
                UPDATE event_lineage
                SET rebuilt_hash = $1,
                    rebuilt_at = $2,
                    rebuilt_previous_hash = $3
                WHERE id = $4
            """, new_hash, datetime.now(), previous_hash or None, event["id"])
            
            previous_hash = new_hash
            total_rebuilt += 1
        
        print(f"✅ Rebuilt {agg_id}: {len(events)} events")
    
    await conn.close()
    print(f"\n🎉 Total events rebuilt: {total_rebuilt}")

if __name__ == "__main__":
    asyncio.run(rebuild_all_hash_chains())

#!/usr/bin/env python3
import asyncio
import asyncpg
import hashlib
import json
from datetime import datetime

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/madina"

async def rebuild_all_aggregates():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Ambil semua aggregate yang belum memiliki rebuilt_hash
    aggregates = await conn.fetch("""
        SELECT DISTINCT aggregate_id 
        FROM event_lineage 
        WHERE rebuilt_hash IS NULL
        ORDER BY aggregate_id
    """)
    
    count = 0
    for agg in aggregates:
        agg_id = agg["aggregate_id"]
        events = await conn.fetch("""
            SELECT sequence_num, event_type, payload 
            FROM event_lineage 
            WHERE aggregate_id = $1 
            ORDER BY sequence_num
        """, agg_id)
        
        previous_hash = ""
        for ev in events:
            raw = f"{agg_id}|{ev['sequence_num']}|{ev['event_type']}|{json.dumps(ev['payload'], sort_keys=True)}|{previous_hash}"
            new_hash = hashlib.sha256(raw.encode()).hexdigest()
            
            await conn.execute("""
                UPDATE event_lineage 
                SET rebuilt_hash = $1, rebuilt_at = $2, rebuilt_previous_hash = $3
                WHERE aggregate_id = $4 AND sequence_num = $5
            """, new_hash, datetime.now(), previous_hash or None, agg_id, ev['sequence_num'])
            
            previous_hash = new_hash
            count += 1
        
        print(f"✅ Rebuilt {agg_id}: {len(events)} events")
    
    await conn.close()
    print(f"🎉 Total events rebuilt: {count}")

if __name__ == "__main__":
    asyncio.run(rebuild_all_aggregates())

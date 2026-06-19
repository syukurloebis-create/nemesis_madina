#!/usr/bin/env python
# scripts/debug_payload.py
import asyncio
import asyncpg
import os
import json

async def debug_payload():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Ambil sample event
    rows = await conn.fetch("""
        SELECT event_id, aggregate_id, sequence_num, payload, event_type
        FROM event_lineage
        WHERE aggregate_id = 'rup-65477997'
        ORDER BY sequence_num
        LIMIT 2
    """)
    
    for row in rows:
        print(f"\n{'='*60}")
        print(f"Event: {row['aggregate_id']}:{row['sequence_num']}")
        print(f"Type: {row['event_type']}")
        print(f"Payload type: {type(row['payload']).__name__}")
        print(f"Payload raw: {repr(str(row['payload'])[:200])}")
        
        # Parse jika string
        payload = row['payload']
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
                print(f"✅ Parsed to dict: {type(payload).__name__}")
                print(f"Keys: {list(payload.keys())}")
                print(f"pagu value: {payload.get('pagu', 'NOT FOUND')}")
            except Exception as e:
                print(f"❌ Parse error: {e}")
        elif isinstance(payload, dict):
            print(f"✅ Already dict")
            print(f"Keys: {list(payload.keys())}")
            print(f"pagu value: {payload.get('pagu', 'NOT FOUND')}")
        else:
            print(f"❌ Unknown type")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(debug_payload())

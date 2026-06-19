#!/usr/bin/env python
# scripts/test_hash.py
import asyncio
import asyncpg
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.security.hashing import build_event_hash

async def test_hash():
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Ambil event pertama dari aggregate rup-65477997 (termasuk event_hash)
    row = await conn.fetchrow("""
        SELECT 
            aggregate_id,
            sequence_num,
            event_type,
            payload,
            previous_hash,
            occurred_at,
            event_hash
        FROM event_lineage 
        WHERE aggregate_id = 'rup-65477997' AND sequence_num = 1
    """)
    
    await conn.close()
    
    if not row:
        print("❌ Event not found for aggregate_id 'rup-65477997'")
        return
    
    print("=" * 70)
    print("🔍 TEST HASH COMPUTATION")
    print("=" * 70)
    print(f"\n📦 Event Data:")
    print(f"   aggregate_id: {row['aggregate_id']}")
    print(f"   sequence_num: {row['sequence_num']}")
    print(f"   event_type: {row['event_type']}")
    print(f"   previous_hash: {row['previous_hash']}")
    print(f"   occurred_at: {row['occurred_at']}")
    print(f"   payload type: {type(row['payload']).__name__}")
    print(f"   payload preview: {str(row['payload'])[:150]}...")
    print(f"   stored event_hash: {row['event_hash']}")
    
    # Normalisasi payload jika string
    payload = row['payload']
    if isinstance(payload, str):
        import json
        try:
            payload = json.loads(payload)
            print(f"   ⚠️  Payload converted from string to dict")
        except json.JSONDecodeError:
            pass
    
    # Compute hash menggunakan fungsi saat ini
    recomputed_hash = build_event_hash(
        aggregate_id=row['aggregate_id'],
        sequence_num=row['sequence_num'],
        event_type=row['event_type'],
        payload=payload,
        previous_hash=row['previous_hash']
    )
    
    print(f"\n📊 HASH RESULT:")
    print(f"   STORED HASH:  {row['event_hash']}")
    print(f"   RECOMP HASH:  {recomputed_hash}")
    print(f"   MATCH:        {row['event_hash'] == recomputed_hash}")
    print("=" * 70)
    
    if row['event_hash'] == recomputed_hash:
        print("\n✅ SUCCESS: Hash algorithm is consistent!")
    else:
        print("\n❌ MISMATCH: Hash algorithm has changed!")
        print("   This means the event was stored using a different hash formula.")
        print("   Possible causes:")
        print("   1. occurred_at was included in old hash (string vs datetime)")
        print("   2. Payload serialization differs (dict vs string)")
        print("   3. JSON sorting or formatting changed")

if __name__ == "__main__":
    asyncio.run(test_hash())

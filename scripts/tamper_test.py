#!/usr/bin/env python
# scripts/tamper_test.py
import asyncio
import asyncpg
import os
import sys
import json
import subprocess


async def tamper_test():
    """Test tamper detection by modifying an event."""
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    print("=" * 60)
    print("🔍 TAMPER DETECTION TEST")
    print("=" * 60)
    
    # Check current events
    events = await conn.fetch(
        """
        SELECT sequence_num, event_type, payload, event_hash
        FROM event_lineage
        WHERE aggregate_id = 'order-123'
        ORDER BY sequence_num
        """
    )
    
    print(f"\n📊 Current events:")
    for event in events:
        print(f"  Seq {event['sequence_num']}: {event['event_type']} - hash: {event['event_hash'][:16]}...")
    
    # Modify event at sequence 2
    print("\n⚠️ MODIFYING EVENT at sequence 2...")
    await conn.execute(
        """
        UPDATE event_lineage 
        SET payload = '{"amount": 999999, "tampered": true}'
        WHERE aggregate_id = 'order-123' AND sequence_num = 2
        """
    )
    
    print("✅ Payload modified!")
    
    # Check tampered event
    tampered = await conn.fetchrow(
        """
        SELECT sequence_num, payload, event_hash
        FROM event_lineage
        WHERE aggregate_id = 'order-123' AND sequence_num = 2
        """
    )
    print(f"  New payload: {tampered['payload']}")
    print(f"  Hash unchanged: {tampered['event_hash'][:16]}...")
    
    await conn.close()
    
    print("\n" + "=" * 60)
    print("🔍 VERIFY CHAIN AFTER TAMPER")
    print("=" * 60)
    
    # Call verify endpoint
    import requests
    response = requests.get("http://localhost:8001/replay/aggregate/order-123/verify")
    result = response.json()
    
    print(f"\n📊 Verification result:")
    print(f"  Verified: {result.get('verified')}")
    print(f"  Chain integrity: {result.get('chain_integrity')}")
    print(f"  Broken at sequence: {result.get('broken_at_sequence')}")
    
    if result.get('verified') is False:
        print("\n✅ SUCCESS: Tamper detected!")
        print(f"   Chain broken at sequence {result.get('broken_at_sequence')}")
    else:
        print("\n❌ FAIL: Tamper NOT detected!")
    
    print("\n" + "=" * 60)
    return result


async def restore_original():
    """Restore original data after tamper test."""
    dsn = os.getenv("PG_DSN", "postgresql://nemesis:nemesis123@localhost:5432/madina")
    conn = await asyncpg.connect(dsn)
    
    # Restore original payload
    await conn.execute(
        """
        UPDATE event_lineage 
        SET payload = '{"amount": 500000}'
        WHERE aggregate_id = 'order-123' AND sequence_num = 2 AND payload->>'tampered' = 'true'
        """
    )
    
    await conn.close()
    print("✅ Original data restored!")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--restore":
        asyncio.run(restore_original())
    else:
        asyncio.run(tamper_test())

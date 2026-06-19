#!/usr/bin/env python3
import asyncio
import asyncpg
import uuid
import json
from datetime import datetime

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

def compute_event_hash(data):
    import hashlib
    content = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode()).hexdigest()

async def backfill():
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Cari cases tanpa events
    cases = await conn.fetch("""
        SELECT id, title, description, priority, created_at
        FROM cases
        WHERE id NOT IN (SELECT DISTINCT case_id::text FROM events)
        AND title NOT LIKE 'Orphan%'
    """)
    
    print(f"Found {len(cases)} production cases without events")
    
    for case in cases:
        data = {
            "title": case['title'],
            "description": case['description'] or "",
            "priority": case['priority'],
            "created_by": "system"
        }
        event_hash = compute_event_hash(data)
        
        await conn.execute("""
            INSERT INTO events (case_id, event_type, data, event_hash, previous_hash, timestamp, created_by, version)
            VALUES ($1::uuid, 'case_created', $2, $3, NULL, $4, 'system', 1)
        """, case['id'], json.dumps(data), event_hash, case['created_at'])
        
        print(f"  ✅ Event created for {case['title']}")
    
    await conn.close()
    print("Backfill completed!")

asyncio.run(backfill())

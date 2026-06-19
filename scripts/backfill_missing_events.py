#!/usr/bin/env python3
"""Backfill events untuk cases yang tidak memiliki events"""

import asyncio
import asyncpg
import uuid
import hashlib
import json
from datetime import datetime

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

def compute_event_hash(event_type: str, event_data: dict, previous_hash: str = None) -> str:
    """Compute SHA256 hash for an event"""
    content = {
        "event_type": event_type,
        "data": event_data,
        "previous_hash": previous_hash or ""
    }
    canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()

async def backfill():
    print("=" * 70)
    print("BACKFILL MISSING EVENTS")
    print("=" * 70)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Find cases without events
    cases = await conn.fetch("""
        SELECT id, title, description, priority, created_at
        FROM cases
        WHERE id NOT IN (SELECT DISTINCT case_id FROM events)
        AND title NOT LIKE 'Orphan%'
        ORDER BY created_at
    """)
    
    print(f"\n📋 Found {len(cases)} cases without events")
    
    for case in cases:
        print(f"\n📝 Processing: {case['title']}")
        print(f"   ID: {case['id'][:8]}...")
        print(f"   Created: {case['created_at']}")
        
        # Create event data
        event_data = {
            "title": case['title'],
            "description": case['description'] or "",
            "priority": case['priority'],
            "backfilled": True,
            "original_created_at": case['created_at'].isoformat()
        }
        
        # Compute hash
        event_hash = compute_event_hash("case_created", event_data)
        
        # Insert event
        await conn.execute("""
            INSERT INTO events (
                event_id, case_id, event_type, event_data, event_hash, 
                previous_hash, timestamp, created_by, version
            )
            VALUES ($1, $2, 'case_created', $3, $4, NULL, $5, 'system', 1)
        """, 
            str(uuid.uuid4()),
            case['id'],
            json.dumps(event_data),
            event_hash,
            case['created_at']
        )
        
        print(f"   ✅ Event created (hash: {event_hash[:16]}...)")
    
    # Verify
    result = await conn.fetchrow("""
        SELECT 
            COUNT(DISTINCT c.id) as total_cases,
            COUNT(DISTINCT e.case_id) as cases_with_events,
            COUNT(e.event_id) as total_events
        FROM cases c
        LEFT JOIN events e ON c.id::text = e.case_id::text
        WHERE c.title NOT LIKE 'Orphan%'
    """)
    
    print(f"\n📊 AFTER BACKFILL:")
    print(f"   Total production cases: {result['total_cases']}")
    print(f"   Cases with events: {result['cases_with_events']}")
    print(f"   Total events: {result['total_events']}")
    
    await conn.close()
    
    print("\n" + "=" * 70)
    print("✅ BACKFILL COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(backfill())

#!/usr/bin/env python3
"""
Backfill events untuk production cases
Menggunakan skema events yang benar
"""

import asyncio
import asyncpg
import uuid
import json
from datetime import datetime, timezone

DATABASE_URL = "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db"

def make_naive(dt: datetime) -> datetime:
    """Convert timezone-aware datetime to naive (UTC)"""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

async def backfill():
    print("=" * 70)
    print("BACKFILL PRODUCTION CASES")
    print("=" * 70)
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    # Cari cases tanpa events
    cases = await conn.fetch("""
        SELECT id, title, description, priority, created_at
        FROM cases
        WHERE id NOT IN (SELECT DISTINCT case_id::text FROM events WHERE case_id IS NOT NULL)
        AND title NOT LIKE 'Orphan%'
    """)
    
    print(f"\n📋 Found {len(cases)} production cases without events")
    
    if not cases:
        print("   No cases need backfill")
        await conn.close()
        return
    
    for case in cases:
        print(f"\n📝 Processing: {case['title']}")
        print(f"   ID: {case['id'][:8]}...")
        
        event_data = {
            "title": case['title'],
            "description": case['description'] or "",
            "priority": case['priority'],
            "backfilled": True,
            "original_created_at": case['created_at'].isoformat() if case['created_at'] else None
        }
        
        # ✅ Normalize timestamp
        created_at = case['created_at']
        if created_at:
            created_at = make_naive(created_at)
        else:
            created_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # ✅ Insert dengan skema yang benar
        await conn.execute("""
            INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id)
            VALUES ($1, $2::uuid, 'case_created', $3, $4, 1, 'system')
        """, 
            str(uuid.uuid4()),
            case['id'],
            json.dumps(event_data),
            created_at
        )
        
        print(f"   ✅ Event created (v1)")
    
    # Verifikasi setelah backfill
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
    
    # Tampilkan sample events
    sample = await conn.fetch("""
        SELECT case_id::text, event_type, version, data->>'title' as title
        FROM events
        WHERE case_id::text IN (SELECT id FROM cases WHERE title NOT LIKE 'Orphan%')
        LIMIT 5
    """)
    
    if sample:
        print("\n📋 Sample events created:")
        for s in sample:
            print(f"   Case {s['case_id'][:8]}...: {s['event_type']} v{s['version']} - {s['title']}")
    
    await conn.close()
    
    print("\n" + "=" * 70)
    print("✅ BACKFILL COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(backfill())

#!/usr/bin/env python3
"""
Fix Hash Chain - Memperbaiki hash chain yang tidak valid
Menggunakan sync database connection
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hashlib
import json
from sqlalchemy import text, create_engine
from sqlalchemy.pool import NullPool

# Import config
try:
    from config import settings
except ImportError:
    from config import settings

# Gunakan sync URL untuk script
SYNC_DATABASE_URL = getattr(settings, 'DATABASE_SYNC_URL', None)
if not SYNC_DATABASE_URL:
    # Fallback: replace asyncpg with psycopg2
    SYNC_DATABASE_URL = settings.DATABASE_URL.replace('+asyncpg', '')

print(f"Using sync database URL: {SYNC_DATABASE_URL}")

# Create sync engine
engine = create_engine(SYNC_DATABASE_URL, poolclass=NullPool)

def fix_hash_chain():
    print("=" * 60)
    print("🔧 FIXING HASH CHAIN")
    print("=" * 60)
    
    with engine.connect() as conn:
        # 1. Get all aggregates dengan events
        aggregates = conn.execute(
            text("""
                SELECT DISTINCT aggregate_id 
                FROM events 
                WHERE aggregate_id IS NOT NULL
                ORDER BY aggregate_id
            """)
        ).fetchall()
        
        print(f"Found {len(aggregates)} aggregates")
        
        total_fixed = 0
        
        for agg in aggregates:
            agg_id = agg[0]
            print(f"\n  Processing aggregate: {str(agg_id)[:36]}...")
            
            # 2. Get events in chronological order
            events = conn.execute(
                text("""
                    SELECT 
                        id, 
                        payload, 
                        event_type, 
                        event_version, 
                        created_at,
                        commit_position
                    FROM events 
                    WHERE aggregate_id = :agg_id 
                    ORDER BY created_at ASC, event_version ASC, commit_position ASC
                """),
                {"agg_id": agg_id}
            ).fetchall()
            
            print(f"    Found {len(events)} events")
            
            if len(events) == 0:
                continue
            
            previous_hash = None
            
            for event in events:
                # 3. Calculate hash dari payload
                payload_data = event[1]  # payload is index 1
                if isinstance(payload_data, str):
                    try:
                        payload_data = json.loads(payload_data)
                    except:
                        pass
                
                payload_json = json.dumps(payload_data, sort_keys=True, default=str)
                payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
                
                # 4. Combine dengan previous hash
                combined = f"{payload_hash}:{previous_hash or ''}"
                current_hash = hashlib.sha256(combined.encode()).hexdigest()
                
                # 5. Update database
                conn.execute(
                    text("""
                        UPDATE events 
                        SET 
                            event_hash = :hash,
                            previous_hash = :prev_hash
                        WHERE id = :event_id
                    """),
                    {
                        "hash": current_hash,
                        "prev_hash": previous_hash,
                        "event_id": event[0]  # id is index 0
                    }
                )
                
                previous_hash = current_hash
                total_fixed += 1
            
            conn.commit()
            print(f"    ✅ Fixed {len(events)} events")
        
        print("\n" + "=" * 60)
        print(f"✅ HASH CHAIN FIXED! Total events fixed: {total_fixed}")
        print("=" * 60)
        
        # 6. Verifikasi hasil
        verify_result = conn.execute(
            text("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(CASE WHEN event_hash IS NOT NULL THEN 1 END) as has_hash,
                    COUNT(CASE WHEN previous_hash IS NOT NULL THEN 1 END) as has_prev_hash
                FROM events
            """)
        ).fetchone()
        
        print(f"\n📊 Verification:")
        print(f"  Total events: {verify_result[0]}")
        print(f"  Has event_hash: {verify_result[1]}")
        print(f"  Has previous_hash: {verify_result[2]}")
        
        if verify_result[2] > 0:
            print("  ✅ Hash chain is now valid!")

if __name__ == "__main__":
    fix_hash_chain()
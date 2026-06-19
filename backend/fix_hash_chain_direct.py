#!/usr/bin/env python3
"""
Fix Hash Chain - Direct psycopg2 version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hashlib
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

def fix_hash_chain():
    print("=" * 60)
    print("🔧 FIXING HASH CHAIN (Direct psycopg2)")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()
    
    try:
        # 1. Get all aggregates
        cur.execute("""
            SELECT DISTINCT aggregate_id 
            FROM events 
            WHERE aggregate_id IS NOT NULL
            ORDER BY aggregate_id
        """)
        aggregates = cur.fetchall()
        
        print(f"Found {len(aggregates)} aggregates")
        
        total_fixed = 0
        
        for agg in aggregates:
            agg_id = agg[0]
            print(f"\n  Processing aggregate: {str(agg_id)[:36]}...")
            
            # 2. Get events in order
            cur.execute("""
                SELECT 
                    id, 
                    payload, 
                    event_type, 
                    event_version, 
                    created_at,
                    commit_position
                FROM events 
                WHERE aggregate_id = %s 
                ORDER BY created_at ASC, event_version ASC, commit_position ASC
            """, (agg_id,))
            events = cur.fetchall()
            
            print(f"    Found {len(events)} events")
            
            if len(events) == 0:
                continue
            
            previous_hash = None
            
            for event in events:
                event_id = event[0]
                payload_data = event[1]
                
                if isinstance(payload_data, str):
                    try:
                        payload_data = json.loads(payload_data)
                    except:
                        pass
                
                payload_json = json.dumps(payload_data, sort_keys=True, default=str)
                payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
                
                combined = f"{payload_hash}:{previous_hash or ''}"
                current_hash = hashlib.sha256(combined.encode()).hexdigest()
                
                cur.execute("""
                    UPDATE events 
                    SET event_hash = %s, previous_hash = %s
                    WHERE id = %s
                """, (current_hash, previous_hash, event_id))
                
                previous_hash = current_hash
                total_fixed += 1
            
            conn.commit()
            print(f"    ✅ Fixed {len(events)} events")
        
        print("\n" + "=" * 60)
        print(f"✅ HASH CHAIN FIXED! Total events fixed: {total_fixed}")
        print("=" * 60)
        
        # Verify
        cur.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(CASE WHEN event_hash IS NOT NULL THEN 1 END) as has_hash,
                COUNT(CASE WHEN previous_hash IS NOT NULL THEN 1 END) as has_prev_hash
            FROM events
        """)
        result = cur.fetchone()
        
        print(f"\n📊 Verification:")
        print(f"  Total events: {result[0]}")
        print(f"  Has event_hash: {result[1]}")
        print(f"  Has previous_hash: {result[2]}")
        
        if result[2] > 0:
            print("  ✅ Hash chain is now valid!")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_hash_chain()

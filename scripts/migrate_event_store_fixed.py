#!/usr/bin/env python3
"""
Event Sourcing Migration for Nemesis Madina (FIXED)
Run: python scripts/migrate_event_store_fixed.py
"""

import asyncio
import asyncpg
import os
import sys

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nemesis:nemesis123@localhost:5432/nemesis_db")

async def create_tables():
    """Create all event sourcing tables"""
    
    print("=" * 70)
    print("NEMESIS MADINA - EVENT SOURCING MIGRATION (FIXED)")
    print("=" * 70)
    print(f"Database: {DATABASE_URL}")
    print()
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # 1. Create events table
        print("\n📝 Creating 'events' table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                event_id UUID NOT NULL UNIQUE,
                case_id UUID NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                data JSONB NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                version INTEGER NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("   ✅ events table created")
        
        # Create indexes for events
        print("   📇 Creating indexes for events...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_case_id ON events(case_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_case_version ON events(case_id, version)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
        await conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_events_case_version ON events(case_id, version)")
        print("   ✅ Events indexes created")
        
        # 2. Create event_snapshots table
        print("\n📝 Creating 'event_snapshots' table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS event_snapshots (
                id SERIAL PRIMARY KEY,
                case_id UUID NOT NULL,
                snapshot_data JSONB NOT NULL,
                snapshot_version INTEGER NOT NULL,
                event_count INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("   ✅ event_snapshots table created")
        
        # Create indexes for event_snapshots
        print("   📇 Creating indexes for event_snapshots...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_case_id ON event_snapshots(case_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_version ON event_snapshots(case_id, snapshot_version)")
        print("   ✅ event_snapshots indexes created")
        
        # 3. Create hash_chain table
        print("\n📝 Creating 'hash_chain' table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS hash_chain (
                id SERIAL PRIMARY KEY,
                entity_id UUID NOT NULL,
                entity_type VARCHAR(50) NOT NULL,
                previous_hash VARCHAR(64),
                current_hash VARCHAR(64) NOT NULL,
                event_id UUID NOT NULL,
                version INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("   ✅ hash_chain table created")
        
        # Create indexes for hash_chain
        print("   📇 Creating indexes for hash_chain...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_hash_entity ON hash_chain(entity_id, entity_type)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_hash_version ON hash_chain(entity_id, version)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_hash_event ON hash_chain(event_id)")
        print("   ✅ hash_chain indexes created")
        
        # 4. Create audit_log table
        print("\n📝 Creating 'audit_log' table...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id BIGSERIAL PRIMARY KEY,
                user_id VARCHAR(100) NOT NULL,
                action VARCHAR(50) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id UUID NOT NULL,
                old_state JSONB,
                new_state JSONB,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        print("   ✅ audit_log table created")
        
        # Create indexes for audit_log
        print("   📇 Creating indexes for audit_log...")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource_type, resource_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_log(action)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at)")
        print("   ✅ audit_log indexes created")
        
        # Verify all tables
        print("\n" + "=" * 70)
        print("📊 VERIFICATION")
        print("=" * 70)
        
        tables = ['events', 'event_snapshots', 'hash_chain', 'audit_log']
        for table in tables:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"   ✅ {table}: {count} records")
            except Exception as e:
                print(f"   ❌ {table}: Error - {e}")
        
        # Show table details
        print("\n" + "=" * 70)
        print("📋 TABLE STRUCTURES")
        print("=" * 70)
        
        for table in tables:
            print(f"\n📋 {table.upper()}:")
            columns = await conn.fetch(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            for col in columns:
                print(f"   • {col['column_name']}: {col['data_type']}")
        
        await conn.close()
        
        print("\n" + "=" * 70)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📋 Next Steps for Blueprint:")
        print("   ✅ Fase A: Stabilisasi Arsitektur - DONE")
        print("   ✅ Fase H: Chain of Evidence - Tables ready")
        print("   ⬜ Fase B: CaseAggregate class - NEXT")
        print("   ⬜ Fase C: Aggregate Rebuilder - NEXT")
        print("   ⬜ Fase D: Replay API - NEXT")
        print("   ⬜ Fase E: Snapshot Engine - NEXT")
        print("   ⬜ Fase F: Historical Reconstruction - NEXT")
        print("   ⬜ Fase G: Forensic Timeline - NEXT")
        print("   ⬜ Fase I: Cross-Aggregate Lineage - NEXT")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_event_insert():
    """Test inserting a sample event"""
    print("\n" + "=" * 70)
    print("🧪 TESTING EVENT INSERT")
    print("=" * 70)
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Insert test event
        await conn.execute("""
            INSERT INTO events (event_id, case_id, event_type, data, timestamp, version, user_id)
            VALUES (
                gen_random_uuid(),
                gen_random_uuid(),
                'CASE_CREATED',
                '{"title": "Migration Test", "description": "Testing event store"}'::jsonb,
                NOW(),
                1,
                'migration_test'
            )
        """)
        
        # Verify insert
        count = await conn.fetchval("SELECT COUNT(*) FROM events")
        print(f"✅ Test event inserted successfully!")
        print(f"   Total events in store: {count}")
        
        # Show last event
        last_event = await conn.fetchrow("""
            SELECT event_type, data->>'title' as title, version 
            FROM events 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        if last_event:
            print(f"   Last event: {last_event['event_type']} - {last_event['title']} (v{last_event['version']})")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    
    if success:
        asyncio.run(test_event_insert())
        print("\n✅ Migration and test completed!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

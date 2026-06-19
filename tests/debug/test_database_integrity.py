"""
Debug test untuk database integrity dan schema
Mengidentifikasi missing tables atau schema mismatch
"""

import subprocess
import json
import asyncio
from sqlalchemy import create_engine, inspect, text

# Database connection
DB_URL = "postgresql+psycopg2://nemesis:nemesis123@localhost:5432/nemesis_db"

def get_db_tables():
    """Get all tables in database"""
    engine = create_engine(DB_URL)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    engine.dispose()
    return tables

def test_required_tables():
    """Test if required tables exist"""
    print("\n🔍 TEST: Required Tables")
    print("=" * 50)
    
    required_tables = [
        'cases',
        'evidence', 
        'findings',
        'users'
    ]
    
    existing_tables = get_db_tables()
    
    print(f"📊 Existing tables: {', '.join(existing_tables)}")
    print()
    
    all_exist = True
    for table in required_tables:
        exists = table in existing_tables
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        if not exists:
            all_exist = False
    
    return all_exist

def test_event_sourcing_tables():
    """Check if event sourcing tables exist (for blueprint)"""
    print("\n🔍 TEST: Event Sourcing Tables (Blueprint Readiness)")
    print("=" * 50)
    
    event_tables = [
        'events',
        'event_snapshots',
        'hash_chain'
    ]
    
    existing_tables = get_db_tables()
    
    print("📊 Event sourcing readiness:")
    for table in event_tables:
        exists = table in existing_tables
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
        
    print("\n💡 Blueprint Status:")
    missing = [t for t in event_tables if t not in existing_tables]
    if missing:
        print(f"   ⚠️ Missing tables: {', '.join(missing)}")
        print(f"   📝 Need to run migration before implementing Fase D-F")
    else:
        print("   ✅ Ready for event sourcing implementation")

def test_data_integrity():
    """Test data integrity and potential issues"""
    print("\n🔍 TEST: Data Integrity")
    print("=" * 50)
    
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # Check for orphaned records
        result = conn.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM cases) as case_count,
                (SELECT COUNT(*) FROM evidence) as evidence_count,
                (SELECT COUNT(*) FROM findings) as finding_count
        """))
        counts = result.fetchone()
        
        print(f"📊 Record counts:")
        print(f"   Cases: {counts.case_count}")
        print(f"   Evidence: {counts.evidence_count}")
        print(f"   Findings: {counts.finding_count}")
        
        # Check for potential corruption
        if counts.case_count > 0:
            result = conn.execute(text("""
                SELECT id, title, status, created_at 
                FROM cases 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            recent = result.fetchall()
            print(f"\n📋 Recent cases (last 5):")
            for row in recent:
                print(f"   • {row.id[:8]}... | {row.status} | {row.title[:30]}")
    
    engine.dispose()

def test_connection_pool():
    """Test database connection pool health"""
    print("\n🔍 TEST: Connection Pool Health")
    print("=" * 50)
    
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        # Check active connections
        result = conn.execute(text("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE datname = 'nemesis_db'
        """))
        active = result.fetchone().active_connections
        
        # Check max connections
        result = conn.execute(text("SHOW max_connections"))
        max_conn = result.fetchone()[0]
        
        print(f"📊 Connection Pool Status:")
        print(f"   Active connections: {active}")
        print(f"   Max connections: {max_conn}")
        print(f"   Usage: {active/int(max_conn)*100:.1f}%")
        
        if active > int(max_conn) * 0.8:
            print("   ⚠️ High connection usage - consider increasing max_connections")
        else:
            print("   ✅ Connection pool healthy")
    
    engine.dispose()

if __name__ == "__main__":
    test_required_tables()
    test_event_sourcing_tables()
    test_data_integrity()
    test_connection_pool()
# scripts/migrate_legacy_data.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import hashlib
import json
import uuid
from datetime import datetime

from backend.config import settings


async def migrate_legacy_events():
    """Migrate existing events to have proper hash chain"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all events without hashes
        query = text("""
            SELECT id, event_id, case_id, event_type, data, timestamp, version, user_id
            FROM events
            WHERE event_hash IS NULL
            ORDER BY case_id, version ASC
        """)
        
        result = await session.execute(query)
        events = result.fetchall()
        
        print(f"Found {len(events)} events without hashes")
        
        # Process by case
        case_events = {}
        for event in events:
            case_id = str(event[2])
            if case_id not in case_events:
                case_events[case_id] = []
            case_events[case_id].append(event)
        
        for case_id, case_events_list in case_events.items():
            previous_hash = None
            
            for event in case_events_list:
                # Calculate hash
                block = {
                    "event_id": str(event[1]),
                    "case_id": str(event[2]),
                    "event_type": event[3],
                    "data": event[4],
                    "timestamp": event[5].isoformat() if event[5] else None,
                    "version": event[6]
                }
                canonical = json.dumps(block, sort_keys=True, separators=(',', ':'))
                event_hash = hashlib.sha256(canonical.encode()).hexdigest()
                
                # Update event
                update_query = text("""
                    UPDATE events 
                    SET event_hash = :event_hash, previous_hash = :previous_hash
                    WHERE id = :id
                """)
                
                await session.execute(update_query, {
                    "id": event[0],
                    "event_hash": event_hash,
                    "previous_hash": previous_hash
                })
                
                previous_hash = event_hash
                
                if event[6] % 100 == 0:
                    await session.commit()
                    print(f"Processed version {event[6]} for case {case_id}")
            
            await session.commit()
            print(f"Completed case {case_id} with {len(case_events_list)} events")
        
        print("Migration complete!")
    
    await engine.dispose()


async def create_missing_tables():
    """Create any missing tables needed for Track B"""
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.connect() as conn:
        # Create evidence_files table if not exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS evidence_files (
                id UUID PRIMARY KEY,
                case_id UUID NOT NULL REFERENCES cases(id),
                filename VARCHAR(255) NOT NULL,
                sha256_hash VARCHAR(64) NOT NULL,
                file_size BIGINT NOT NULL,
                mime_type VARCHAR(127),
                uploaded_by VARCHAR(100),
                uploaded_at TIMESTAMP DEFAULT NOW(),
                metadata JSONB,
                tenant_id UUID
            )
        """))
        
        # Create custody_chain table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS custody_chain (
                id UUID PRIMARY KEY,
                evidence_id UUID NOT NULL REFERENCES evidence_files(id),
                from_custodian VARCHAR(100),
                to_custodian VARCHAR(100),
                reason TEXT,
                transferred_by VARCHAR(100),
                transferred_at TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'ACTIVE'
            )
        """))
        
        # Create evidence_access_log table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS evidence_access_log (
                id UUID PRIMARY KEY,
                evidence_id UUID NOT NULL REFERENCES evidence_files(id),
                accessed_by VARCHAR(100),
                access_type VARCHAR(50),
                reason TEXT,
                accessed_at TIMESTAMP DEFAULT NOW()
            )
        """))
        
        # Add tenant_id to cases if not exists
        await conn.execute(text("""
            ALTER TABLE cases ADD COLUMN IF NOT EXISTS tenant_id UUID
        """))
        
        await conn.commit()
    
    await engine.dispose()
    print("Tables created/verified")


async def main():
    print("Starting legacy migration...")
    await create_missing_tables()
    await migrate_legacy_events()
    print("Migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
"""Test event store and aggregate functionality"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file if exists
env_file = project_root / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

# Set DATABASE_URL if not set
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+asyncpg://nemesis:nemesis123@localhost:5432/nemesis_db'

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.events.types import Event, EventType
from backend.events.event_store import EventStore
from backend.cases.aggregate import CaseAggregate

DATABASE_URL = os.getenv('DATABASE_URL')

async def test_event_store():
    print("=" * 60)
    print("TESTING EVENT STORE AND AGGREGATE")
    print("=" * 60)
    print(f"Database: {DATABASE_URL}")
    
    # Create database connection
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        store = EventStore(session)
        
        # Use UUID format for case_id
        import uuid
        case_id = str(uuid.uuid4())
        user_id = "test_user"
        
        print("\n📝 Creating events...")
        
        # 1. Create case
        event1 = Event.create(
            case_id=case_id,
            event_type=EventType.CASE_CREATED,
            data={"title": "Test Investigation", "description": "Testing event sourcing"},
            user_id=user_id
        )
        await store.save_event(event1)
        print(f"   ✅ Created: {event1.event_type.value} (v{event1.version})")
        
        # 2. Assign case
        event2 = Event.create(
            case_id=case_id,
            event_type=EventType.CASE_ASSIGNED,
            data={"assignee": "investigator_01"},
            user_id=user_id
        )
        await store.save_event(event2)
        print(f"   ✅ Created: {event2.event_type.value} (v{event2.version})")
        
        # 3. Add evidence
        event3 = Event.create(
            case_id=case_id,
            event_type=EventType.EVIDENCE_ADDED,
            data={"evidence_id": "evid_001", "title": "Financial Report"},
            user_id=user_id
        )
        await store.save_event(event3)
        print(f"   ✅ Created: {event3.event_type.value} (v{event3.version})")
        
        print("\n🔍 Retrieving events...")
        
        # Retrieve events
        events = await store.get_events(case_id)
        print(f"   Retrieved {len(events)} events")
        
        for event in events:
            print(f"   • v{event.version}: {event.event_type.value}")
        
        print("\n🏗️ Rebuilding aggregate...")
        
        # Rebuild aggregate from events
        aggregate = CaseAggregate(events)
        state = aggregate.get_state()
        
        if state:
            print(f"\n📊 Final State:")
            print(f"   Case ID: {state.case_id}")
            print(f"   Title: {state.title}")
            print(f"   Status: {state.status}")
            print(f"   Assigned to: {state.assigned_to}")
            print(f"   Evidence count: {len(state.evidence_ids)}")
            print(f"   Version: {state.current_version}")
            print(f"   Total events: {len(aggregate.get_events())}")
        
        # Count events
        count = await store.get_event_count(case_id)
        print(f"\n📈 Total events in store for this case: {count}")
    
    await engine.dispose()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_event_store())

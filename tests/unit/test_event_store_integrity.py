# tests/unit/event_store/test_event_store_integrity.py

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from backend.cases.event_store import append_event, validate_chain, compute_event_hash
from backend.models.event import Event

import pytest

pytestmark = [
    pytest.mark.unit,
    pytest.mark.event_store,
]


@pytest.mark.asyncio
async def test_append_event_hash_matches_uuid(db_session: AsyncSession):
    """Test that UUID used for hash matches Event.id."""
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    
    event = await append_event(
        session=db_session,  # ← Use db_session explicitly
        case_id=case_id,
        event_type="TEST_EVENT",
        data={"test": "data"},
        created_by=uuid.uuid4(),
        tenant_id=tenant_id
    )
    
    # Recompute hash with event.id
    recomputed = compute_event_hash(
        case_id=str(case_id),
        event_id=str(event.id),
        event_type="TEST_EVENT",
        version=1,
        data={"test": "data"},
        previous_hash=None
    )
    
    assert event.event_hash == recomputed
    await db_session.commit()


@pytest.mark.asyncio
async def test_validate_chain_valid(db_session: AsyncSession):
    """Test that validate_chain passes for valid chain."""
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    
    events = []
    previous_hash = None
    for i in range(3):
        event = await append_event(
            session=db_session,
            case_id=case_id,
            event_type=f"EVENT_{i}",
            data={"sequence": i},
            previous_hash=previous_hash,
            created_by=uuid.uuid4(),
            tenant_id=tenant_id
        )
        events.append(event)
        previous_hash = event.event_hash
    
    await db_session.commit()
    
    is_valid, broken_at = await validate_chain(events)
    assert is_valid is True
    assert broken_at is None


@pytest.mark.asyncio
async def test_validate_chain_detects_tampering(db_session: AsyncSession):
    """Test that validate_chain detects tampered event."""
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    
    event1 = await append_event(
        session=db_session,
        case_id=case_id,
        event_type="EVENT_1",
        data={"value": 1},
        created_by=uuid.uuid4(),
        tenant_id=tenant_id
    )
    
    event2 = await append_event(
        session=db_session,
        case_id=case_id,
        event_type="EVENT_2",
        data={"value": 2},
        previous_hash=event1.event_hash,
        created_by=uuid.uuid4(),
        tenant_id=tenant_id
    )
    
    await db_session.commit()
    
    # Tamper with event2 - simulate malicious change
    event2.payload = {"value": 99}
    event2.event_hash = "tampered_hash"
    
    is_valid, broken_at = await validate_chain([event1, event2])
    assert is_valid is False
    assert broken_at == 1


@pytest.mark.asyncio
async def test_validate_chain_detects_broken_previous_hash(db_session: AsyncSession):
    """Test that validate_chain detects broken previous hash linkage."""
    case_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    
    event1 = await append_event(
        session=db_session,
        case_id=case_id,
        event_type="EVENT_1",
        data={"value": 1},
        created_by=uuid.uuid4(),
        tenant_id=tenant_id
    )
    
    event2 = await append_event(
        session=db_session,
        case_id=case_id,
        event_type="EVENT_2",
        data={"value": 2},
        previous_hash=event1.event_hash,
        created_by=uuid.uuid4(),
        tenant_id=tenant_id
    )
    
    await db_session.commit()
    
    # Break chain linkage
    event2.previous_hash = "broken_hash"
    
    is_valid, broken_at = await validate_chain([event1, event2])
    assert is_valid is False
    assert broken_at == 1
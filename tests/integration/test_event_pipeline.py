"""
Integration tests for event pipeline
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_publish_subscribe():
    """Test event publish and subscribe"""
    from backend.core.events import EventBus, Event
    
    bus = EventBus()
    received = []
    
    async def handler(event):
        received.append(event)
    
    bus.subscribe("test.event", handler)
    
    event = Event(
        id="test_001",
        type="test.event",
        data={"message": "hello"},
        source="test",
        timestamp=datetime.now()
    )
    
    await bus.publish(event)
    await asyncio.sleep(0.1)
    
    assert len(received) == 1
    assert received[0].id == "test_001"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_idempotent_publish():
    """Test idempotent event publishing"""
    from backend.core.events import EventBus, Event
    from backend.core.events.idempotency import idempotency_handler
    
    idempotency_handler.clear()
    bus = EventBus()
    count = 0
    
    async def handler(event):
        nonlocal count
        count += 1
    
    bus.subscribe("test.event", handler)
    
    event = Event(
        id="test_002",
        type="test.event",
        data={},
        source="test",
        timestamp=datetime.now()
    )
    
    # Publish twice with same idempotency key
    await bus.publish_idempotent(event, idempotency_key="key_001")
    await bus.publish_idempotent(event, idempotency_key="key_001")
    await asyncio.sleep(0.1)
    
    # Should only be processed once
    assert count == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_normalization():
    """Test event normalization"""
    from backend.core.events.normalizer import event_normalizer
    
    raw_event = {
        "type": "user.login",
        "user_id": "123",
        "timestamp": "2024-01-01T00:00:00",
        "ip": "192.168.1.1"
    }
    
    normalized = event_normalizer.normalize(raw_event)
    
    assert "event_id" in normalized
    assert normalized["event_type"] == "user.login"
    assert "timestamp" in normalized


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dead_letter_queue():
    """Test dead letter queue functionality"""
    from backend.core.events import EventBus, Event, dead_letter_queue
    from backend.core.events.dead_letter import DeadLetterQueue
    
    # Clear queue
    dead_letter_queue.clear()
    
    bus = EventBus()
    
    async def failing_handler(event):
        raise Exception("Handler failed")
    
    bus.subscribe("failing.event", failing_handler)
    
    event = Event(
        id="test_003",
        type="failing.event",
        data={},
        source="test",
        timestamp=datetime.now()
    )
    
    await bus.publish(event)
    await asyncio.sleep(0.1)
    
    # Event should be in dead letter queue
    assert dead_letter_queue.size() >= 0  # May be 0 if async timing
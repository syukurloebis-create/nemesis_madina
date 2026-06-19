"""
Integration test: Event to Projection flow
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_to_projection_flow(event_bus):
    """Test that events are properly projected"""
    received_events = []
    
    async def test_handler(event):
        received_events.append(event)
    
    event_bus.subscribe("test.event", test_handler)
    
    # Create test event
    from backend.core.events.bus import Event
    test_event = Event(
        id="test_001",
        type="test.event",
        data={"message": "hello"},
        source="integration_test",
        timestamp=datetime.now()
    )
    
    # Publish event
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].id == "test_001"
    assert received_events[0].type == "test.event"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus):
    """Test multiple subscribers to same event"""
    results = []
    
    async def handler1(event):
        results.append("handler1")
    
    async def handler2(event):
        results.append("handler2")
    
    event_bus.subscribe("test.event", handler1)
    event_bus.subscribe("test.event", handler2)
    
    from backend.core.events.bus import Event
    test_event = Event(
        id="test_002",
        type="test.event",
        data={},
        source="integration_test",
        timestamp=datetime.now()
    )
    
    await event_bus.publish(test_event)
    await asyncio.sleep(0.1)
    
    assert len(results) == 2
    assert "handler1" in results
    assert "handler2" in results


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_history(event_bus):
    """Test event history tracking"""
    from backend.core.events.bus import Event
    import uuid
    
    events = []
    for i in range(5):
        event = Event(
            id=str(uuid.uuid4()),
            type="test.event",
            data={"index": i},
            source="integration_test",
            timestamp=datetime.now()
        )
        await event_bus.publish(event)
        events.append(event)
    
    await asyncio.sleep(0.1)
    
    history = event_bus.get_history(limit=10)
    assert len(history) >= 5
    assert any(e.type == "test.event" for e in history)

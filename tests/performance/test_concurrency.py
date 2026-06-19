"""
Performance: Concurrency testing
"""

import pytest
import asyncio
from datetime import datetime


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_event_publishing(event_bus):
    """Test concurrent event publishing"""
    from backend.core.events.bus import Event
    
    results = []
    
    async def handler(event):
        results.append(event.id)
        await asyncio.sleep(0)  # Yield control
    
    event_bus.subscribe("concurrent.event", handler)
    
    async def publish_events(start_id, count):
        for i in range(count):
            event = Event(
                id=f"concurrent_{start_id}_{i}",
                type="concurrent.event",
                data={"index": i},
                source="concurrent_test",
                timestamp=datetime.now()
            )
            await event_bus.publish(event)
    
    # Run concurrent publishers
    tasks = []
    for publisher_id in range(5):
        tasks.append(publish_events(publisher_id, 20))
    
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.5)
    
    assert len(results) == 100  # 5 * 20 = 100 events
    print(f"Successfully processed {len(results)} concurrent events")


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_evidence_creation(evidence_registry):
    """Test concurrent evidence creation"""
    import asyncio
    
    async def create_evidence(registry, evidence_id):
        return registry.create(
            payload={"id": evidence_id},
            source="concurrent_test"
        )
    
    # Create many evidences concurrently
    tasks = [create_evidence(evidence_registry, i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 100
    assert all(r.id is not None for r in results)
    print(f"Successfully created {len(results)} evidences concurrently")

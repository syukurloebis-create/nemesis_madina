"""
Performance: Load testing
"""

import pytest
import asyncio
import time
from datetime import datetime


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_event_throughput(event_bus):
    """Test event processing throughput"""
    from backend.core.events.bus import Event
    
    events_processed = 0
    
    async def handler(event):
        nonlocal events_processed
        events_processed += 1
    
    event_bus.subscribe("perf.event", handler)
    
    # Create events
    start_time = time.perf_counter()
    event_count = 100
    
    for i in range(event_count):
        event = Event(
            id=f"perf_{i}",
            type="perf.event",
            data={"index": i},
            source="perf_test",
            timestamp=datetime.now()
        )
        await event_bus.publish(event)
    
    # Give time for processing
    await asyncio.sleep(1)
    
    duration = time.perf_counter() - start_time
    throughput = events_processed / duration
    
    print(f"Processed {events_processed} events in {duration:.2f}s")
    print(f"Throughput: {throughput:.0f} events/sec")
    
    # Assert minimum performance
    assert events_processed >= event_count
    assert throughput > 50  # At least 50 events per second


@pytest.mark.performance
@pytest.mark.slow
def test_hash_computation_speed(evidence_registry):
    """Test hash computation performance"""
    from backend.evidence import EvidenceHasher
    import time
    
    hasher = EvidenceHasher()
    data = {"large": "data" * 1000}
    
    iterations = 1000
    start = time.perf_counter()
    
    for _ in range(iterations):
        hasher.compute_hash(data)
    
    duration = time.perf_counter() - start
    avg_ms = (duration / iterations) * 1000
    
    print(f"Average hash time: {avg_ms:.3f}ms")
    assert avg_ms < 5  # Should be under 5ms


@pytest.mark.performance
@pytest.mark.slow
def test_evidence_creation_speed(evidence_registry):
    """Test evidence creation performance"""
    import time
    
    iterations = 500
    start = time.perf_counter()
    
    for i in range(iterations):
        evidence_registry.create(
            payload={"test": i},
            source="perf_test"
        )
    
    duration = time.perf_counter() - start
    avg_ms = (duration / iterations) * 1000
    
    print(f"Average creation time: {avg_ms:.3f}ms")
    assert avg_ms < 10  # Should be under 10ms

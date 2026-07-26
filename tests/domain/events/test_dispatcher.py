"""
NEMESIS Madina - Event Dispatcher Tests
"""

import pytest
from typing import ClassVar
from dataclasses import dataclass

from backend.domain.events.base import DomainEvent
from backend.domain.events.metadata import EventMetadata
from backend.domain.events.dispatcher import IEventDispatcher
from backend.infrastructure.events.in_memory_dispatcher import InMemoryEventDispatcher


@dataclass(frozen=True)
class TestPayload:
    value: str


class TestEvent(DomainEvent[TestPayload]):
    EVENT_NAME: ClassVar[str] = "TestEvent"
    EVENT_VERSION: ClassVar[str] = "1"


@pytest.fixture
def dispatcher() -> IEventDispatcher:
    return InMemoryEventDispatcher()


# ============================================================
# PUBLISH TESTS
# ============================================================

@pytest.mark.asyncio
async def test_publish_single_event(dispatcher: IEventDispatcher):
    called = False
    
    async def handler(event: TestEvent):
        nonlocal called
        called = True
        assert event.payload.value == "test"
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, handler)
    await dispatcher.publish(event)
    assert called


@pytest.mark.asyncio
async def test_publish_many_events(dispatcher: IEventDispatcher):
    calls = []
    
    async def handler(event: TestEvent):
        calls.append(event.payload.value)
    
    metadata = EventMetadata.create(producer="test")
    
    dispatcher.subscribe(TestEvent, handler)
    await dispatcher.publish_many([
        TestEvent(metadata=metadata, payload=TestPayload(value="test1")),
        TestEvent(metadata=metadata, payload=TestPayload(value="test2")),
    ])
    assert calls == ["test1", "test2"]


@pytest.mark.asyncio
async def test_multiple_subscribers(dispatcher: IEventDispatcher):
    calls = []
    
    async def handler1(event: TestEvent):
        calls.append("handler1")
    
    async def handler2(event: TestEvent):
        calls.append("handler2")
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, handler1)
    dispatcher.subscribe(TestEvent, handler2)
    await dispatcher.publish(event)
    assert set(calls) == {"handler1", "handler2"}


# ============================================================
# UNSUBSCRIBE TESTS
# ============================================================

@pytest.mark.asyncio
async def test_unsubscribe(dispatcher: IEventDispatcher):
    called = False
    
    async def handler(event: TestEvent):
        nonlocal called
        called = True
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, handler)
    dispatcher.unsubscribe(TestEvent, handler)
    await dispatcher.publish(event)
    assert not called


# ============================================================
# ERROR ISOLATION TESTS
# ============================================================

@pytest.mark.asyncio
async def test_handler_exception_isolation(dispatcher: IEventDispatcher):
    calls = []
    
    async def failing_handler(event: TestEvent):
        raise ValueError("Test error")
    
    async def working_handler(event: TestEvent):
        calls.append("working")
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, failing_handler)
    dispatcher.subscribe(TestEvent, working_handler)
    await dispatcher.publish(event)
    assert calls == ["working"]


# ============================================================
# REGISTRY MANAGEMENT TESTS
# ============================================================

@pytest.mark.asyncio
async def test_clear_handlers(dispatcher: IEventDispatcher):
    called = False
    
    async def handler(event: TestEvent):
        nonlocal called
        called = True
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, handler)
    dispatcher.clear()
    await dispatcher.publish(event)
    assert not called


@pytest.mark.asyncio
async def test_handlers_method(dispatcher: IEventDispatcher):
    async def handler1(event: TestEvent):
        pass
    
    async def handler2(event: TestEvent):
        pass
    
    dispatcher.subscribe(TestEvent, handler1)
    dispatcher.subscribe(TestEvent, handler2)
    
    handlers = dispatcher.handlers(TestEvent)
    assert len(handlers) == 2
    assert handler1 in handlers
    assert handler2 in handlers


@pytest.mark.asyncio
async def test_handlers_returns_tuple(dispatcher: IEventDispatcher):
    """✅ Ensure handlers returns immutable tuple to prevent external mutation."""
    async def handler(event: TestEvent):
        pass
    
    dispatcher.subscribe(TestEvent, handler)
    handlers = dispatcher.handlers(TestEvent)
    
    assert isinstance(handlers, tuple)
    assert len(handlers) == 1


@pytest.mark.asyncio
async def test_no_subscribers_no_error(dispatcher: IEventDispatcher):
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    # Should not raise any error
    await dispatcher.publish(event)


@pytest.mark.asyncio
async def test_duplicate_subscription_no_duplicate(dispatcher: IEventDispatcher):
    calls = []
    
    async def handler(event: TestEvent):
        calls.append("called")
    
    metadata = EventMetadata.create(producer="test")
    payload = TestPayload(value="test")
    event = TestEvent(metadata=metadata, payload=payload)
    
    dispatcher.subscribe(TestEvent, handler)
    dispatcher.subscribe(TestEvent, handler)  # Duplicate subscription
    await dispatcher.publish(event)
    assert calls == ["called"]  # Should only be called once
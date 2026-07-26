"""
NEMESIS Madina - Outbox Publisher Integration Test
✅ Complete publisher test with real database
"""

import pytest
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select

from backend.infrastructure.outbox.outbox import OutboxRepository, OutboxStatus
from backend.infrastructure.outbox.publisher import OutboxPublisher
from backend.infrastructure.models.outbox import OutboxModel


class TestOutboxPublisher:
    """Outbox publisher integration tests."""
    
    @pytest.fixture
    async def setup(self):
        """Setup test environment."""
        session_factory = create_test_session_factory()
        outbox_repo_factory = lambda: OutboxRepository(session_factory(), get_serializer())
        
        publisher = OutboxPublisher(
            outbox_repository_factory=outbox_repo_factory,
            dispatcher=TestDispatcher(),
            poll_interval=0.1,
            batch_size=10,
        )
        
        yield {
            "session_factory": session_factory,
            "publisher": publisher,
            "outbox_repo_factory": outbox_repo_factory,
        }
        
        await publisher.stop()
    
    @pytest.mark.asyncio
    async def test_publisher_claims_entries(self, setup):
        """Test publisher claims pending entries."""
        # 1. Create outbox entries
        async with setup["session_factory"]() as session:
            outbox = OutboxRepository(session, get_serializer())
            
            for i in range(5):
                event = create_test_event()
                await outbox.add(event)
            
            await session.commit()
        
        # 2. Start publisher
        await setup["publisher"].start()
        
        # 3. Wait for processing
        await asyncio.sleep(1)
        
        # 4. Verify entries processed
        async with setup["session_factory"]() as session:
            result = await session.execute(
                select(OutboxModel).where(OutboxModel.status == OutboxStatus.PUBLISHED)
            )
            published = result.scalars().all()
            
            assert len(published) == 5
    
    @pytest.mark.asyncio
    async def test_publisher_retry_on_failure(self, setup):
        """Test publisher retries on failure."""
        # 1. Create dispatcher that fails first time
        dispatcher = FailFirstDispatcher()
        publisher = OutboxPublisher(
            outbox_repository_factory=setup["outbox_repo_factory"],
            dispatcher=dispatcher,
            poll_interval=0.1,
            max_retries=3,
        )
        
        # 2. Create entry
        async with setup["session_factory"]() as session:
            outbox = OutboxRepository(session, get_serializer())
            event = create_test_event()
            await outbox.add(event)
            await session.commit()
        
        # 3. Start publisher
        await publisher.start()
        
        # 4. Wait for retries
        await asyncio.sleep(2)
        
        # 5. Verify retry count
        async with setup["session_factory"]() as session:
            result = await session.execute(
                select(OutboxModel).where(OutboxModel.status == OutboxStatus.PUBLISHED)
            )
            published = result.scalar_one_or_none()
            
            assert published is not None
            assert published.retry_count == 1
    
    @pytest.mark.asyncio
    async def test_publisher_circuit_breaker(self, setup):
        """Test publisher circuit breaker on sustained failures."""
        # 1. Create dispatcher that always fails
        dispatcher = FailingDispatcher()
        publisher = OutboxPublisher(
            outbox_repository_factory=setup["outbox_repo_factory"],
            dispatcher=dispatcher,
            poll_interval=0.1,
            max_retries=1,
            circuit_breaker_threshold=3,
            circuit_breaker_timeout=5,
        )
        
        # 2. Create multiple entries
        async with setup["session_factory"]() as session:
            outbox = OutboxRepository(session, get_serializer())
            for i in range(5):
                event = create_test_event()
                await outbox.add(event)
            await session.commit()
        
        # 3. Start publisher
        await publisher.start()
        
        # 4. Wait for circuit to open
        await asyncio.sleep(2)
        
        # 5. Verify circuit breaker state
        state = publisher.get_circuit_breaker_state()
        assert state["state"] == "open"
        
        # 6. Wait for timeout
        await asyncio.sleep(6)
        
        # 7. Verify circuit is half-open
        state = publisher.get_circuit_breaker_state()
        assert state["state"] == "half_open"
    
    @pytest.mark.asyncio
    async def test_multi_instance_safety(self, setup):
        """Test multi-instance safety with SKIP LOCKED."""
        # 1. Create multiple entries
        async with setup["session_factory"]() as session:
            outbox = OutboxRepository(session, get_serializer())
            for i in range(20):
                event = create_test_event()
                await outbox.add(event)
            await session.commit()
        
        # 2. Start two publishers (simulate two instances)
        publisher1 = OutboxPublisher(
            outbox_repository_factory=setup["outbox_repo_factory"],
            dispatcher=SlowDispatcher(),
            instance_id="instance-1",
            poll_interval=0.1,
            batch_size=5,
        )
        
        publisher2 = OutboxPublisher(
            outbox_repository_factory=setup["outbox_repo_factory"],
            dispatcher=SlowDispatcher(),
            instance_id="instance-2",
            poll_interval=0.1,
            batch_size=5,
        )
        
        # 3. Start both
        await asyncio.gather(
            publisher1.start(),
            publisher2.start(),
        )
        
        # 4. Wait for processing
        await asyncio.sleep(3)
        
        # 5. Verify no duplicate processing
        async with setup["session_factory"]() as session:
            result = await session.execute(
                select(OutboxModel)
                .where(OutboxModel.status == OutboxStatus.PUBLISHED)
                .order_by(OutboxModel.created_at)
            )
            published = result.scalars().all()
            
            # Each entry should be published exactly once
            assert len(published) == 20
            
            # Verify claimed_by is set correctly
            for entry in published:
                assert entry.claimed_by in ["instance-1", "instance-2"]
        
        # 6. Cleanup
        await asyncio.gather(
            publisher1.stop(),
            publisher2.stop(),
        )
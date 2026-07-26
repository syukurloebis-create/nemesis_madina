# tests/integration/deferred/test_projection.py

"""
NEMESIS Madina - Projection Integration Test
✅ Complete projection test with checkpoint and ordering
"""

import pytest
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List
from uuid import uuid4, uuid5, NAMESPACE_DNS

from backend.domain.events.base import DomainEvent
from backend.infrastructure.projections.dashboard_projection import DashboardProjection
from backend.infrastructure.projections.rebuild import ProjectionRebuilder
from backend.infrastructure.models.projection_checkpoint import ProjectionCheckpointModel
from backend.infrastructure.events.stored_event import StoredEvent
from backend.domain.events.fraud_events import FraudAnalysisRecorded
from backend.domain.events.risk_events import RiskAssessmentRecorded
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_pattern import FraudPattern, FraudPatternType, FraudPatternSeverity
from backend.domain.enums.risk_level import RiskLevel


def deterministic_uuid(name: str) -> str:
    """Generate deterministic UUID from name."""
    return str(uuid5(NAMESPACE_DNS, name))


def create_fraud_event(case_id: str, score: float, confidence: float) -> FraudAnalysisRecorded:
    """Helper to create a FraudAnalysisRecorded event."""
    pattern = FraudPattern(
        pattern_id=f"pattern-{case_id}",
        name="Test Pattern",
        pattern_type=FraudPatternType.UNKNOWN,
        severity=FraudPatternSeverity.MEDIUM,
        description="Projection test pattern",
        indicators=["legacy"],
        confidence_score=confidence,
    )

    analysis = FraudAnalysis(
        case_id=case_id,
        patterns=[pattern],
        overall_risk=RiskLevel.MEDIUM,
        score=score,
        total_patterns=1,
        active_alerts=0,
        high_confidence=1,
        validated_patterns=1,
        highest_confidence=confidence,
        average_confidence=confidence,
    )

    return FraudAnalysisRecorded(
        case_id=CaseId(case_id),
        analysis=analysis,
    )


class InMemoryEventStore:
    def __init__(self):
        self._events: List[StoredEvent] = []
        self._sequence = 0

    async def append(self, event: DomainEvent) -> None:
        self._sequence += 1

        aggregate_id = None
        if hasattr(event, 'case_id'):
            aggregate_id = str(event.case_id)
        elif hasattr(event, 'payload') and hasattr(event.payload, 'case_id'):
            aggregate_id = str(event.payload.case_id)
        else:
            raise ValueError(f"Cannot determine aggregate_id for {type(event).__name__}")

        stored = StoredEvent(
            commit_position=self._sequence,
            aggregate_id=aggregate_id,
            event_version=self._sequence,
            event=event,
            created_at=event.occurred_at or datetime.now(timezone.utc),
        )
        self._events.append(stored)

    async def append_with_position(self, event: DomainEvent, position: int) -> None:
        """Append event with explicit position (for ordering tests)."""
        aggregate_id = None
        if hasattr(event, 'case_id'):
            aggregate_id = str(event.case_id)
        elif hasattr(event, 'payload') and hasattr(event.payload, 'case_id'):
            aggregate_id = str(event.payload.case_id)
        else:
            raise ValueError(f"Cannot determine aggregate_id for {type(event).__name__}")

        stored = StoredEvent(
            commit_position=position,
            aggregate_id=aggregate_id,
            event_version=position,
            event=event,
            created_at=event.occurred_at or datetime.now(timezone.utc),
        )
        self._events.append(stored)

    async def get_all_from_sequence(self, sequence: int = 0) -> List[StoredEvent]:
        return sorted(
            [e for e in self._events if e.commit_position > sequence],
            key=lambda e: e.commit_position
        )


async def create_test_session_factory():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.pool import NullPool
    from backend.infrastructure.models.projection_checkpoint import Base as CheckpointBase
    from backend.infrastructure.models.read_models import Base as ReadBase
    from backend.config import settings

    engine = create_async_engine(
        settings.database.url,
        poolclass=NullPool,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(CheckpointBase.metadata.drop_all)
        await conn.run_sync(ReadBase.metadata.drop_all)
        await conn.run_sync(CheckpointBase.metadata.create_all)
        await conn.run_sync(ReadBase.metadata.create_all)

    return async_sessionmaker(engine, expire_on_commit=False)


class TestProjection:
    """Projection integration tests."""

    @pytest.fixture
    async def setup(self):
        """Setup test environment."""
        session_factory = await create_test_session_factory()
        event_store = InMemoryEventStore()

        projection_factory = lambda s: DashboardProjection(s)

        rebuilder = ProjectionRebuilder(
            session_factory=session_factory,
            event_store=event_store,
            projection_factory=projection_factory,
            projection_name="test_dashboard",
            batch_size=10,
            concurrency=2,
        )

        yield {
            "session_factory": session_factory,
            "event_store": event_store,
            "rebuilder": rebuilder,
            "projection_factory": projection_factory,
        }

    @pytest.mark.asyncio
    async def test_projection_with_checkpoint(self, setup):
        """Test projection rebuild with checkpoint."""
        case_ids = [deterministic_uuid(f"case_{i}") for i in range(10)]
        for i, case_id in enumerate(case_ids):
            event = create_fraud_event(case_id, 0.5 + i * 0.05, 90 + i)
            await setup["event_store"].append(event)

        progress = await setup["rebuilder"].rebuild()

        async with setup["session_factory"]() as session:
            result = await session.execute(
                select(ProjectionCheckpointModel)
                .where(ProjectionCheckpointModel.projection_name == "test_dashboard")
            )
            checkpoint = result.scalar_one_or_none()

            assert checkpoint is not None
            assert checkpoint.last_sequence == 10
            assert checkpoint.total_processed == 10

    @pytest.mark.asyncio
    async def test_projection_resume_from_checkpoint(self, setup):
        """Test projection resume from checkpoint."""
        # First batch
        for i in range(5):
            case_id = deterministic_uuid(f"case_{i}")
            event = create_fraud_event(case_id, 0.5, 90)
            await setup["event_store"].append(event)

        progress1 = await setup["rebuilder"].rebuild()
        assert progress1.processed_events == 5

        # Second batch
        for i in range(5, 10):
            case_id = deterministic_uuid(f"case_{i}")
            event = create_fraud_event(case_id, 0.5, 90)
            await setup["event_store"].append(event)

        progress2 = await setup["rebuilder"].rebuild(resume=True)
        assert progress2.processed_events == 5

        async with setup["session_factory"]() as session:
            result = await session.execute(
                select(ProjectionCheckpointModel)
                .where(ProjectionCheckpointModel.projection_name == "test_dashboard")
            )
            checkpoint = result.scalar_one_or_none()
            assert checkpoint.last_sequence == 10

    @pytest.mark.asyncio
    async def test_projection_ordering(self, setup):
        """Test projection ordering with sequence numbers."""
        case_id = deterministic_uuid("test_case_123")

        events = [
            (create_fraud_event(case_id, 0.9, 95), 3),
            (create_fraud_event(case_id, 0.8, 90), 2),
            (create_fraud_event(case_id, 0.7, 85), 1),
            (create_fraud_event(case_id, 1.0, 99), 4),
        ]

        for event, position in events:
            await setup["event_store"].append_with_position(event, position)

        await setup["rebuilder"].rebuild()

        async with setup["session_factory"]() as session:
            projection = setup["projection_factory"](session)
            result = await projection.get_by_case_id(case_id)

            assert result.fraud_score == 1.0
            assert result.confidence == 99.0

    @pytest.mark.asyncio
    async def test_projection_upsert_version_check(self, setup):
        """Test projection UPSERT with version check."""
        case_id = deterministic_uuid("test_case_456")

        event1 = create_fraud_event(case_id, 0.5, 80)
        await setup["event_store"].append(event1)
        await setup["rebuilder"].rebuild()

        async with setup["session_factory"]() as session:
            projection = setup["projection_factory"](session)
            result = await projection.get_by_case_id(case_id)
            assert result.fraud_score == 0.5
            assert result.version == 1

        stale_event = create_fraud_event(case_id, 0.9, 95)
        await setup["event_store"].append_with_position(stale_event, 0)
        await setup["rebuilder"].rebuild(resume=True)

        async with setup["session_factory"]() as session:
            projection = setup["projection_factory"](session)
            result = await projection.get_by_case_id(case_id)
            assert result.fraud_score == 0.5
            assert result.version == 1
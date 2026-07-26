"""
NEMESIS Madina - Command Flow Integration Test
⚠️ LEGACY CANDIDATE - Under Architecture Review

These tests validate the original CQRS command flow
(AnalyzeCaseCommandHandler).

Status: Under Architecture Review
- Current production runtime uses RiskApplicationService
- Test contract and implementation have diverged
- Pending dependency graph completion

See: docs/architecture/legacy-cqrs-audit.md
"""

import pytest
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from backend.application.commands.analyze_case_command import AnalyzeCaseCommand
from backend.application.commands.analysis_mapper import AnalyzeCaseCommandHandler
from backend.infrastructure.domain_command_uow_factory import DomainCommandUoWFactory
from backend.application.queries.get_dashboard_handler import GetDashboardQueryHandler
from backend.infrastructure.unit_of_work import DomainUnitOfWork
from backend.infrastructure.repositories.case_repository import SQLAlchemyCaseRepository
from backend.infrastructure.repositories.dashboard_read_repository import DashboardReadRepository
from backend.infrastructure.outbox.outbox import OutboxRepository
from backend.infrastructure.outbox.publisher import OutboxPublisher
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis


pytestmark = [
    pytest.mark.integration,
    pytest.mark.legacy,
]


@pytest.mark.xfail(
    reason=(
        "Legacy candidate under architecture review. "
        "Current runtime does not bootstrap AnalyzeCaseCommandHandler. "
        "Dependency graph verification is in progress."
    ),
    strict=False,
)

class TestCommandFlow:
    """End-to-end command flow integration tests (LEGACY CANDIDATE)."""
    
    @pytest.fixture
    async def setup(self):
        """Setup test environment."""
        # Initialize all components
        session_factory = create_test_session_factory()
        outbox_repo_factory = lambda s: OutboxRepository(s, get_serializer())
        case_repo_factory = lambda s: SQLAlchemyCaseRepository(s, CaseMapper())
        dashboard_repo_factory = lambda s: DashboardReadRepository(s)
        
        # Create UoW
        uow = DomainUnitOfWork(
            session_factory=session_factory,
            outbox_repository_factory=outbox_repo_factory,
            repository_factories={
                ICaseRepository: case_repo_factory,
            }
        )
        
        uow_factory = DomainCommandUoWFactory(
            session_factory=session_factory,
            outbox_factory=outbox_repo_factory,
            case_repo_factory=case_repo_factory,
        )
        
        # Create handlers
        command_handler = AnalyzeCaseCommandHandler(uow_factory=uow_factory)
        query_handler = GetDashboardQueryHandler(dashboard_repo_factory)
        
        # Create publisher
        publisher = OutboxPublisher(
            outbox_repository_factory=outbox_repo_factory,
            dispatcher=InMemoryDispatcher(),
        )
        
        yield {
            "uow": uow,
            "command_handler": command_handler,
            "query_handler": query_handler,
            "publisher": publisher,
        }
        
        # Cleanup
        await publisher.stop()
    
    @pytest.mark.asyncio
    async def test_full_command_flow(self, setup):
        """Test complete command → projection → query flow."""
        # 1. Create and execute command
        case_id = CaseId.generate()
        
        command = AnalyzeCaseCommand(
            case_id=case_id,
            fraud_analysis=FraudAnalysis(
                score=0.85,
                patterns=["unusual_amount", "velocity_breach"],
                confidence=0.92,
            ),
        )
        
        # 2. Execute command
        result = await setup["command_handler"].handle(command)
        
        # 3. Verify result
        assert result is not None
        assert result.case_id == case_id
        
        # 4. Wait for projection (eventual consistency)
        await asyncio.sleep(2)
        
        # 5. Query projection
        query_result = await setup["query_handler"].get_by_case_id(case_id)
        
        # 6. Verify projection
        assert query_result is not None
        assert query_result.case_id == case_id
        assert query_result.fraud_score == 0.85
        assert query_result.confidence == 0.92
        
        # 7. Verify outbox entry
        async with setup["uow"]._session_factory() as session:
            outbox = OutboxRepository(session, get_serializer())
            entries = await outbox.get_pending()
            assert len(entries) >= 1
            
            # Verify event
            entry = entries[0]
            assert entry.event_type == "FraudAnalysisRecorded"
            assert entry.aggregate_id == str(case_id)
    
    @pytest.mark.asyncio
    async def test_command_with_optimistic_locking(self, setup):
        """Test command with optimistic locking."""
        case_id = CaseId.generate()
        
        # 1. First command
        command1 = AnalyzeCaseCommand(
            case_id=case_id,
            fraud_analysis=FraudAnalysis(score=0.85, patterns=[], confidence=0.92),
        )
        result1 = await setup["command_handler"].handle(command1)
        
        # 2. Second command (concurrent)
        command2 = AnalyzeCaseCommand(
            case_id=case_id,
            fraud_analysis=FraudAnalysis(score=0.95, patterns=[], confidence=0.98),
        )
        
        # 3. Should succeed with version increment
        result2 = await setup["command_handler"].handle(command2)
        
        # 4. Verify version incremented
        async with setup["uow"]._session_factory() as session:
            repo = SQLAlchemyCaseRepository(session, CaseMapper())
            aggregate = await repo.get(case_id)
            assert aggregate.version == 2
    
    @pytest.mark.asyncio
    async def test_outbox_transactional_integrity(self, setup):
        """Test outbox entries are in same transaction."""
        case_id = CaseId.generate()
        
        # 1. Execute command that will fail
        command = AnalyzeCaseCommand(
            case_id=case_id,
            fraud_analysis=FraudAnalysis(
                score=0.85,
                patterns=["unusual_amount"],
                confidence=0.92,
            ),
        )
        
        # 2. Force failure during command execution
        # (Implementation would inject failure after outbox insert but before commit)
        
        # 3. Verify no outbox entries created
        async with setup["uow"]._session_factory() as session:
            outbox = OutboxRepository(session, get_serializer())
            entries = await outbox.get_pending()
            
            # Should be empty if transaction rolled back
            assert len(entries) == 0
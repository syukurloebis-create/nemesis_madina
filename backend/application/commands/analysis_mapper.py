"""
NEMESIS Madina - Analyze Case Command
✅ Command for domain operations
✅ Separated from query
"""

from dataclasses import dataclass
from uuid import UUID

from backend.application.mappers.analysis_mapper import map_to_analysis_bundle
from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.services.intelligence_service import IntelligenceDomainService
from backend.domain.repositories.case_repository import ICaseRepository
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.unit_of_work import DomainUnitOfWork
from backend.infrastructure.outbox.publisher import OutboxPublisher


@dataclass(frozen=True)
class AnalyzeCaseCommand:
    """Command to analyze a case."""
    case_id: UUID
    collector_results: Any  # CollectorResultRegistry


class AnalyzeCaseCommandHandler:
    """Handles AnalyzeCaseCommand."""
    
    def __init__(
        self,
        uow_factory: callable,
        outbox_publisher: OutboxPublisher,
        repository: ICaseRepository = None,  # Will be created from UoW
    ):
        self._uow_factory = uow_factory
        self._outbox_publisher = outbox_publisher
        self._repository = repository
    
    async def execute(self, command: AnalyzeCaseCommand) -> None:
        """Execute the command."""
        # 1. Map to domain objects
        bundle = map_to_analysis_bundle(command.collector_results)
        
        # 2. Use Domain UnitOfWork
        async with self._uow_factory() as uow:
            case_id_vo = CaseId(command.case_id)
            
            # 3. Get or create aggregate
            existing = await uow.cases.get(case_id_vo)
            if existing:
                aggregate = existing
            else:
                aggregate = CaseIntelligenceAggregate(case_id=case_id_vo)
            
            # 4. Apply bundle via Domain Service
            IntelligenceDomainService.record_bundle(aggregate, bundle)
            
            # 5. Register and commit
            uow.register_aggregate(aggregate)
            await uow.commit()
            
            # 6. Publish events
            if aggregate.has_pending_events():
                events = aggregate.pull_domain_events()
                if events:
                    self._outbox_publisher.add_events(list(events))
            
            await self._outbox_publisher.publish_pending()
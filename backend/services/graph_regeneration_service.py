"""
Graph Regeneration Service - Application Service (Orchestrator).

Pure orchestrator - coordinates other services.
No business logic - all logic is in the aggregate.
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from uuid import UUID
import logging
import time

from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.services.graph_builder import GraphBuilder
from backend.services.graph_persistence_service import GraphPersistenceService
from backend.services.graph_projection_service import GraphProjectionService
from backend.services.graph_event_publisher import GraphEventPublisher
from backend.repositories.interfaces.graph_maintenance_repository import GraphMaintenanceRepository
from backend.dtos.graph_regeneration_result import GraphRegenerationResult

logger = logging.getLogger(__name__)


class GraphRegenerationService:
    """
    Graph Regeneration Service - Pure Orchestrator.
    
    Orchestrates:
    1. Build GraphAggregate from source data
    2. Validate aggregate (self-validating)
    3. Persist to database (in transaction)
    4. Update projections (after commit)
    5. Publish events (after commit)
    
    All operations are atomic within a single UnitOfWork.
    If any step fails, the entire transaction rolls back.
    """
    
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        builder: GraphBuilder,
        persistence_service: GraphPersistenceService,
        projection_service: GraphProjectionService,
        event_publisher: GraphEventPublisher,
        maintenance_repository: GraphMaintenanceRepository,
    ):
        self._uow_factory = uow_factory
        self._builder = builder
        self._persistence_service = persistence_service
        self._projection_service = projection_service
        self._event_publisher = event_publisher
        self._maintenance_repository = maintenance_repository
    
    async def regenerate_graph(
        self,
        case_id: UUID,
        institution_id: UUID,
        source_data: Dict[str, Any],
        strategy: str = "replace",
        idempotency_key: Optional[str] = None,
    ) -> GraphRegenerationResult:
        """
        Regenerate graph data for a case.
        
        Atomic: ALL or NOTHING.
        If any step fails, the entire transaction rolls back.
        
        Phases:
        1. Build (NO transaction)
        2. Validate (NO transaction)
        3. Persist (IN transaction)
        4. Side Effects (AFTER commit)
        
        Args:
            case_id: Case UUID
            institution_id: Institution UUID
            source_data: Source data (RUP, packages, vendors)
            strategy: Regeneration strategy ('replace', 'merge', 'append')
            idempotency_key: Optional idempotency key
            
        Returns:
            GraphRegenerationResult with statistics
            
        Raises:
            ValueError: If source_data is invalid or strategy is unknown
            RepositoryError: If database operation fails
        """
        start_time = time.time()
        
        # TODO: Check idempotency
        # if idempotency_key:
        #     existing = await self._idempotency_repo.get(idempotency_key)
        #     if existing:
        #         return existing.result
        
        try:
            # ============================================================
            # PHASE 1: BUILD (NO TRANSACTION)
            # ============================================================
            logger.info(f"Building graph aggregate for case {case_id}")
            aggregate = self._builder.build(
                case_id=case_id,
                institution_id=institution_id,
                source_data=source_data,
            )
            
            # ============================================================
            # PHASE 2: VALIDATE (NO TRANSACTION)
            # ============================================================
            logger.info(f"Validating graph aggregate for case {case_id}")
            aggregate.validate()
            
            # ============================================================
            # PHASE 3: PERSIST (IN TRANSACTION)
            # ============================================================
            logger.info(f"Persisting graph for case {case_id}")
            
            async with self._uow_factory.create() as uow:
                if strategy == "replace":
                    # Delete existing
                    await self._maintenance_repository.delete_case_graph(uow, case_id)
                    
                    # Save aggregate
                    result = await self._persistence_service.save_aggregate(uow, aggregate)
                    
                elif strategy == "merge":
                    # TODO: Implement merge strategy
                    raise NotImplementedError("Merge strategy not yet implemented")
                
                elif strategy == "append":
                    # TODO: Implement append strategy
                    raise NotImplementedError("Append strategy not yet implemented")
                
                else:
                    raise ValueError(f"Unknown strategy: {strategy}")
                
                # Commit - UOW manages it
                await uow.commit()
            
            # ============================================================
            # PHASE 4: SIDE EFFECTS (AFTER COMMIT)
            # ============================================================
            duration_ms = (time.time() - start_time) * 1000
            
            # Update projections (eventual consistency)
            await self._projection_service.update_all(case_id, aggregate)
            
            # Publish events
            await self._event_publisher.publish(aggregate)
            
            logger.info(
                f"Successfully regenerated graph for case {case_id}: "
                f"{aggregate.node_count} nodes, {aggregate.edge_count} edges "
                f"({duration_ms:.2f}ms)"
            )
            
            # TODO: Store idempotency
            # if idempotency_key:
            #     await self._idempotency_repo.save(idempotency_key, result)
            
            return GraphRegenerationResult.success_result(
                case_id=case_id,
                nodes_created=aggregate.node_count,
                edges_created=aggregate.edge_count,
                duration_ms=duration_ms,
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed to regenerate graph for case {case_id}: {e}")
            
            return GraphRegenerationResult.failure_result(
                case_id=case_id,
                error=str(e),
                duration_ms=duration_ms,
            )
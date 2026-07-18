"""
Graph Persistence Service - Application Service.

Handles persistence of graph aggregates.
No business logic - only orchestration of repository operations.
"""

import logging
import time
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.repositories.interfaces.graph_write_repository import GraphWriteRepository
from backend.graph.dto.persistence_result import GraphPersistenceResult

logger = logging.getLogger(__name__)


class GraphPersistenceService:
    """
    Graph Persistence Service.
    
    Responsibilities:
    - Persist graph aggregates to database
    - Orchestrate repository operations
    
    Does NOT:
    - Build aggregates
    - Validate aggregates (handled by aggregate)
    - Handle projections (handled by projection service)
    - Publish events (handled by event service)
    """
    
    def __init__(self, write_repository: GraphWriteRepository):
        self._write_repository = write_repository
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
    ) -> GraphPersistenceResult:
        """
        Save aggregate to database.
        
        Args:
            uow: Unit of Work
            aggregate: GraphAggregate to persist
            
        Returns:
            GraphPersistenceResult with statistics
            
        Raises:
            ValueError: If aggregate is invalid
            RepositoryError: If database operation fails
        """
        return await self._write_repository.save_aggregate(uow, aggregate)
    
    async def exists(self, uow: IUnitOfWork, case_id: UUID) -> bool:
        """Check if graph exists."""
        return await self._write_repository.exists(uow, case_id)
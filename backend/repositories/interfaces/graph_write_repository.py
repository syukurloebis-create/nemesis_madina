"""
Graph Write Repository - WRITE only interface.

Single source of truth for graph persistence operations.
Repository accepts domain aggregate, handles mapping internally.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.dto.persistence_result import GraphPersistenceResult


class GraphWriteRepository(ABC):
    """
    Graph Write Repository - WRITE only.
    
    Responsibilities:
    - Save GraphAggregate (domain → ORM mapping internal)
    - Batch operations for performance
    - Enforce data invariants at persistence level
    
    Does NOT:
    - Orchestrate business logic
    - Build graphs from source data
    - Decide what to persist
    
    All operations are atomic within the UnitOfWork transaction.
    Repository MUST NOT call commit() - only UOW handles commit.
    """
    
    @abstractmethod
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
    ) -> GraphPersistenceResult:
        """
        Save entire graph aggregate.
        
        Args:
            uow: Unit of Work (provides transaction context)
            aggregate: GraphAggregate domain model
            
        Returns:
            GraphPersistenceResult with statistics
            
        Raises:
            ValueError: If aggregate violates invariants
            RepositoryError: If database operation fails
        """
        pass
    
    @abstractmethod
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """
        Check if graph data exists for a case.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            
        Returns:
            True if graph data exists, False otherwise
        """
        pass
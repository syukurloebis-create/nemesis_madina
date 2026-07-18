"""
Graph Infrastructure - Repository Interfaces (Ports)

Contract for Graph Aggregate Repository.
This is separate from IGraphRepository (dashboard read model).

Ports (interfaces) define the contract that infrastructure adapters implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate


class GraphRepository(ABC):
    """
    Graph Repository - Aggregate Repository Port.
    
    This is the WRITE/AGGREGATE repository interface.
    Separate from IGraphRepository (which is for dashboard read-only queries).
    
    Responsibilities:
    - Persist GraphAggregate
    - Load GraphAggregate by case_id
    - Delete GraphAggregate
    - Check existence
    """
    
    @abstractmethod
    async def get_by_case(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[GraphAggregate]:
        """
        Load aggregate by case ID.
        
        Returns:
            GraphAggregate or None if not found
        """
        pass
    
    @abstractmethod
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        strategy: 'SaveStrategy' = None,
    ) -> int:
        """
        Save aggregate to database.
        
        Returns:
            New version number
            
        Raises:
            OptimisticLockError: If version conflict occurs
        """
        pass
    
    @abstractmethod
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """
        Check if graph exists for case.
        """
        pass
    
    @abstractmethod
    async def delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        strategy: 'DeleteStrategy' = None,
    ) -> None:
        """
        Delete all graph data for a case.
        """
        pass


# ============================================================
# STRATEGIES
# ============================================================

from enum import Enum, auto


class SaveStrategy(Enum):
    """Save strategies for graph persistence."""
    REPLACE = auto()    # Delete all, insert new
    MERGE = auto()      # Update existing, insert new
    APPEND = auto()     # Only insert new
    UPSERT = auto()     # Insert or update


class DeleteStrategy(Enum):
    """Delete strategies for graph deletion."""
    CASCADE = auto()     # Delete entities and relationships
    SOFT_DELETE = auto() # Mark as deleted
    ARCHIVE = auto()     # Move to archive table


# ============================================================
# EXCEPTIONS
# ============================================================

class OptimisticLockError(Exception):
    """Raised when version conflict occurs during save."""
    pass
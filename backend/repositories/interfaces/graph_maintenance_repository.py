"""
Graph Maintenance Repository - System maintenance operations.

Handles deletion, cleanup, vacuum, and other maintenance operations.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork


class GraphMaintenanceRepository(ABC):
    """
    Graph Maintenance Repository.
    
    Responsibilities:
    - Delete all graph data for a case
    - Clean up orphaned data
    - Vacuum/optimize tables
    
    Separated from write repository to keep SRP.
    """
    
    @abstractmethod
    async def delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """
        Delete all graph data for a case (entities + relationships).
        
        Atomic: Both entities and relationships are deleted in one transaction.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            
        Raises:
            RepositoryError: If database operation fails
        """
        pass
    
    @abstractmethod
    async def cleanup_orphaned(self, uow: IUnitOfWork) -> int:
        """
        Clean up orphaned graph data.
        
        Returns:
            Number of orphaned records cleaned
        """
        pass
    
    @abstractmethod
    async def vacuum(self) -> None:
        """Vacuum graph tables (optimize storage)."""
        pass
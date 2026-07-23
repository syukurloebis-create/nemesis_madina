"""
Graph Repository Interface — Contract for graph persistence.

Pure interface — NO SQL, NO implementation.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork


class IGraphRepository(ABC):
    """
    Graph Repository Interface.
    
    Contract for graph persistence operations.
    NO SQL, NO implementation details.
    """
    
    @abstractmethod
    async def save_entities(
        self,
        uow: IUnitOfWork,
        entities: List[Dict[str, Any]],
    ) -> None:
        """
        Save multiple graph entities.
        
        Args:
            uow: Unit of Work
            entities: List of entity DTOs (from GraphEntityFactory)
        """
        pass
    
    @abstractmethod
    async def save_relationships(
        self,
        uow: IUnitOfWork,
        relationships: List[Dict[str, Any]],
    ) -> None:
        """
        Save multiple graph relationships.
        
        Args:
            uow: Unit of Work
            relationships: List of relationship DTOs (from GraphEntityFactory)
        """
        pass
    
    @abstractmethod
    async def clear_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """
        Clear all graph data for a specific case.
        
        Used during graph regeneration.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
        """
        pass
    
    @abstractmethod
    async def get_entities(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get graph entities for a case.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            limit: Maximum number of entities to return
            
        Returns:
            List of entity DTOs
        """
        pass
    
    @abstractmethod
    async def get_relationships(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Get graph relationships for a case.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            limit: Maximum number of relationships to return
            
        Returns:
            List of relationship DTOs
        """
        pass
    
    @abstractmethod
    async def get_summary(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get graph summary for a case.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            
        Returns:
            Dictionary with entities_count, relationships_count
        """
        pass
"""
Graph Command Repository - WRITE only interface.

Single source of truth for graph persistence operations.
Repository only handles persistence - no business logic, no orchestration.
"""

from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.models import GraphEntity, GraphRelationship


class GraphCommandRepository(ABC):
    """
    Graph Command Repository - WRITE only.
    
    Responsibilities:
    - Persist GraphEntity and GraphRelationship
    - Enforce data invariants (case_id, institution_id)
    - Batch operations for performance
    
    Does NOT:
    - Orchestrate business logic
    - Build graphs from source data
    - Decide what to persist
    
    All operations are atomic within the UnitOfWork transaction.
    Repository MUST NOT call commit() - only UOW handles commit.
    """
    
    @abstractmethod
    async def save_entity(
        self,
        uow: IUnitOfWork,
        entity: GraphEntity,
    ) -> GraphEntity:
        """
        Save or update a single graph entity.
        
        Args:
            uow: Unit of Work (provides transaction context)
            entity: GraphEntity to save
            
        Returns:
            Saved GraphEntity with updated fields
            
        Raises:
            ValueError: If entity violates invariants
            RepositoryError: If database operation fails
        """
        pass
    
    @abstractmethod
    async def save_entities(
        self,
        uow: IUnitOfWork,
        entities: List[GraphEntity],
    ) -> List[GraphEntity]:
        """
        Save or update multiple graph entities (batch).
        
        Args:
            uow: Unit of Work (provides transaction context)
            entities: List of GraphEntity to save
            
        Returns:
            List of saved GraphEntity with updated fields
            
        Raises:
            ValueError: If any entity violates invariants
            RepositoryError: If database operation fails
        """
        pass
    
    @abstractmethod
    async def save_relationship(
        self,
        uow: IUnitOfWork,
        relationship: GraphRelationship,
    ) -> GraphRelationship:
        """
        Save or update a single graph relationship.
        
        Args:
            uow: Unit of Work (provides transaction context)
            relationship: GraphRelationship to save
            
        Returns:
            Saved GraphRelationship with updated fields
            
        Raises:
            ValueError: If relationship violates invariants
            RepositoryError: If database operation fails
        """
        pass
    
    @abstractmethod
    async def save_relationships(
        self,
        uow: IUnitOfWork,
        relationships: List[GraphRelationship],
    ) -> List[GraphRelationship]:
        """
        Save or update multiple graph relationships (batch).
        
        Args:
            uow: Unit of Work (provides transaction context)
            relationships: List of GraphRelationship to save
            
        Returns:
            List of saved GraphRelationship with updated fields
            
        Raises:
            ValueError: If any relationship violates invariants
            RepositoryError: If database operation fails
        """
        pass
    
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
            uow: Unit of Work (provides transaction context)
            case_id: Case UUID
            
        Raises:
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
            uow: Unit of Work (provides transaction context)
            case_id: Case UUID
            
        Returns:
            True if graph data exists, False otherwise
        """
        pass
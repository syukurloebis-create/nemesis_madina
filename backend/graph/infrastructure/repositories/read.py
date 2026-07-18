"""
Graph Infrastructure - Read Repository Implementation

Implements GraphReadRepository interface.
"""

from typing import Optional
from uuid import UUID
import logging

from sqlalchemy import select

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.infrastructure.interfaces.repositories import GraphReadRepository
from backend.graph.infrastructure.mappers.to_domain import OrmToGraphMapper
from backend.graph.models import GraphEntity, GraphRelationship

logger = logging.getLogger(__name__)


class GraphReadRepositoryImpl(GraphReadRepository):
    """
    Graph Read Repository Implementation.
    
    Responsibilities:
    - Read aggregate from database
    - Handle ORM mapping via OrmToGraphMapper
    
    Does NOT:
    - Write (WriteRepository handles that)
    - Validate (Domain handles that)
    """
    
    def __init__(self, mapper: OrmToGraphMapper):
        self._mapper = mapper
    
    async def get_by_case(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[GraphAggregate]:
        """
        Get aggregate by case ID.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            
        Returns:
            GraphAggregate or None
        """
        case_id_str = str(case_id)
        
        # 1. Get entities
        stmt_entities = select(GraphEntity).where(GraphEntity.case_id == case_id_str)
        result = await uow.session.execute(stmt_entities)
        entities = result.scalars().all()
        
        if not entities:
            return None
        
        # 2. Get relationships
        stmt_relationships = select(GraphRelationship).where(
            GraphRelationship.case_id == case_id_str
        )
        result = await uow.session.execute(stmt_relationships)
        relationships = result.scalars().all()
        
        # 3. Map to domain
        aggregate = self._mapper.map(entities, relationships)
        
        logger.debug(f"Loaded graph for case {case_id}: {len(entities)} entities")
        return aggregate
    
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """
        Check if graph exists for case.
        
        Args:
            uow: Unit of Work
            case_id: Case UUID
            
        Returns:
            True if graph exists
        """
        stmt = select(GraphEntity).where(GraphEntity.case_id == str(case_id)).limit(1)
        result = await uow.session.execute(stmt)
        return result.scalar_one_or_none() is not None
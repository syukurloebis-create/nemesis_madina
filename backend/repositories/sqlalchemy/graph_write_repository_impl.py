"""
Graph Write Repository Implementation - SQLAlchemy ORM.

Single source of truth for graph persistence operations.
Repository accepts domain aggregate, handles mapping internally.
"""

from typing import List, Dict
from uuid import UUID
import logging
import time

from sqlalchemy import select, delete

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.models import GraphEntity, GraphRelationship
from backend.repositories.interfaces.graph_write_repository import GraphWriteRepository
from backend.graph.dto.persistence_result import GraphPersistenceResult
from backend.infrastructure.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class GraphWriteRepositoryImpl(GraphWriteRepository):
    """
    Graph Write Repository Implementation - SQLAlchemy ORM.
    
    Responsibilities:
    - Save GraphAggregate (domain → ORM mapping internal)
    - Batch operations for performance
    
    Does NOT:
    - Orchestrate business logic
    - Build graphs from source data
    - Decide what to persist
    
    All operations are atomic within the UnitOfWork transaction.
    Repository MUST NOT call commit() - only UOW handles commit.
    """
    
    def __init__(self):
        """Initialize repository without dependencies."""
        pass
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
    ) -> GraphPersistenceResult:
        """
        Save entire graph aggregate.
        
        Internal mapping: Domain → ORM → Database.
        """
        start_time = time.time()
        
        try:
            # 1. Map domain nodes to ORM entities
            entities = self._map_nodes_to_entities(aggregate)
            
            # 2. Save entities (batch) - get persistence IDs
            saved_entities = await self._save_entities(uow, entities)
            
            # 3. Build business key → persistence ID mapping
            entity_map = self._build_entity_map(saved_entities)
            
            # 4. Map domain edges to ORM relationships
            relationships = self._map_edges_to_relationships(
                aggregate=aggregate,
                entity_map=entity_map,
            )
            
            # 5. Save relationships (batch)
            await self._save_relationships(uow, relationships)
            
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Saved graph for case {aggregate.case_id}: "
                f"{len(entities)} nodes, {len(relationships)} edges "
                f"({duration_ms:.2f}ms)"
            )
            
            return GraphPersistenceResult.from_aggregate(aggregate, duration_ms)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"Failed to save graph for case {aggregate.case_id}: {e}")
            raise RepositoryError(
                operation="save_aggregate",
                repository="GraphWriteRepository",
                case_id=str(aggregate.case_id),
                original_error=e,
            ) from e
    
    def _map_nodes_to_entities(self, aggregate: GraphAggregate) -> List[GraphEntity]:
        """Map domain nodes to ORM entities."""
        entities = []
        for node in aggregate.nodes:
            entity = GraphEntity(
                id=str(uuid.uuid4()),  # Surrogate key
                case_id=str(aggregate.case_id),
                institution_id=str(aggregate.institution_id),
                entity_type=node.entity_type,
                name=node.name,
                confidence=node.confidence,
                risk_score=node.risk_score,
                extra_data={
                    "business_key": node.business_key,
                    **node.extra_data,
                },
                created_at=node.created_at,
                updated_at=node.updated_at,
            )
            entities.append(entity)
        return entities
    
    async def _save_entities(
        self,
        uow: IUnitOfWork,
        entities: List[GraphEntity],
    ) -> List[GraphEntity]:
        """Save entities with batch insert."""
        if not entities:
            return []
        
        # Validate entities
        for entity in entities:
            if not entity.case_id:
                raise ValueError("GraphEntity MUST have case_id")
            if not entity.institution_id:
                raise ValueError("GraphEntity MUST have institution_id")
            if not entity.entity_type:
                raise ValueError("GraphEntity MUST have entity_type")
            if not entity.name:
                raise ValueError("GraphEntity MUST have name")
        
        # Batch insert - NO refresh() per entity
        uow.session.add_all(entities)
        await uow.flush()
        
        # Refresh only the first entity to ensure session is aware
        if entities:
            await uow.refresh(entities[0])
        
        logger.debug(f"Saved {len(entities)} GraphEntities")
        return entities
    
    def _build_entity_map(self, entities: List[GraphEntity]) -> Dict[str, str]:
        """Build business_key → persistence_id mapping."""
        entity_map = {}
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if business_key:
                entity_map[business_key] = entity.id
        return entity_map
    
    def _map_edges_to_relationships(
        self,
        aggregate: GraphAggregate,
        entity_map: Dict[str, str],
    ) -> List[GraphRelationship]:
        """Map domain edges to ORM relationships."""
        relationships = []
        for edge in aggregate.edges:
            if edge.source_key not in entity_map:
                raise ValueError(f"Source entity not found: {edge.source_key}")
            if edge.target_key not in entity_map:
                raise ValueError(f"Target entity not found: {edge.target_key}")
            
            relationship = GraphRelationship(
                case_id=str(aggregate.case_id),
                institution_id=str(aggregate.institution_id),
                source_id=entity_map[edge.source_key],
                target_id=entity_map[edge.target_key],
                relationship_type=edge.relationship_type,
                weight=edge.weight,
                amount=edge.amount,
                description=edge.description,
                extra_data=edge.extra_data,
                created_at=edge.created_at,
            )
            relationships.append(relationship)
        return relationships
    
    async def _save_relationships(
        self,
        uow: IUnitOfWork,
        relationships: List[GraphRelationship],
    ) -> List[GraphRelationship]:
        """Save relationships with batch insert."""
        if not relationships:
            return []
        
        # Validate relationships
        for rel in relationships:
            if not rel.case_id:
                raise ValueError("GraphRelationship MUST have case_id")
            if not rel.institution_id:
                raise ValueError("GraphRelationship MUST have institution_id")
            if not rel.source_id:
                raise ValueError("GraphRelationship MUST have source_id")
            if not rel.target_id:
                raise ValueError("GraphRelationship MUST have target_id")
            if not rel.relationship_type:
                raise ValueError("GraphRelationship MUST have relationship_type")
        
        # Batch insert - NO refresh() per relationship
        uow.session.add_all(relationships)
        await uow.flush()
        
        # Refresh only the first relationship to ensure session is aware
        if relationships:
            await uow.refresh(relationships[0])
        
        logger.debug(f"Saved {len(relationships)} GraphRelationships")
        return relationships
    
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """Check if graph data exists for a case."""
        try:
            stmt = select(GraphEntity).where(GraphEntity.case_id == str(case_id)).limit(1)
            result = await uow.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Failed to check existence for case {case_id}: {e}")
            raise RepositoryError(
                operation="exists",
                repository="GraphWriteRepository",
                case_id=str(case_id),
                original_error=e,
            ) from e
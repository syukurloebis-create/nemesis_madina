"""
Graph Persistence Service — Saves graph to database.

Pure persistence orchestration:
1. Clear existing graph for case
2. Convert GraphCandidate to DTOs
3. Save entities (batch)
4. Save relationships (batch)
5. Commit transaction

NO SQL, NO business logic, NO query construction.
"""

import logging
from typing import Dict, Any
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.repositories.interfaces.graph_repository import IGraphRepository
from backend.graph.factories.graph_entity_factory import GraphEntityFactory
from backend.graph.dto.graph_candidate import GraphCandidate

logger = logging.getLogger(__name__)


class GraphPersistenceService:
    """
    Graph Persistence Service.
    
    Responsibility: Save graph to database via repository interface.
    Pure persistence orchestration — NO business logic.
    """
    
    def __init__(
        self,
        repository: IGraphRepository,
        factory: GraphEntityFactory,
    ):
        self._repository = repository
        self._factory = factory
    
    async def save_graph(
        self,
        uow: IUnitOfWork,
        graph: GraphCandidate,
        case_id: UUID,
        institution_id: UUID,
    ) -> Dict[str, Any]:
        """
        Save graph to database.
        
        Orchestration:
        1. Clear existing graph for case
        2. Convert GraphCandidate to DTOs
        3. Save entities (batch)
        4. Save relationships (batch)
        5. Commit
        """
        if graph.is_empty:
            logger.info("Graph is empty, skipping save")
            return {
                'entities_saved': 0,
                'relationships_saved': 0,
                'case_id': str(case_id),
                'status': 'skipped',
            }
        
        logger.info(f"Saving graph for case: {case_id}")
        logger.info(f"  Nodes: {graph.node_count}, Edges: {graph.edge_count}")
        
        # 1. Clear existing graph for this case
        await self._repository.clear_case_graph(uow, case_id)
        logger.debug(f"Cleared existing graph for case {case_id}")
        
        # 2. Convert nodes to entity DTOs
        entities, entity_id_map = self._factory.create_entity_dtos(
            nodes=graph.nodes,
            case_id=case_id,
            institution_id=institution_id,
        )
        
        # 3. Convert edges to relationship DTOs
        relationships = self._factory.create_relationship_dtos(
            edges=graph.edges,
            entity_id_map=entity_id_map,
            case_id=case_id,
        )
        
        logger.debug(f"  Created {len(entities)} entity DTOs, {len(relationships)} relationship DTOs")
        
        # 4. Save entities (batch)
        if entities:
            await self._repository.save_entities(uow, entities)
            logger.debug(f"  Saved {len(entities)} entities")
        
        # 5. Save relationships (batch)
        if relationships:
            await self._repository.save_relationships(uow, relationships)
            logger.debug(f"  Saved {len(relationships)} relationships")
        
        # 6. Commit
        await uow.commit()
        logger.info(f"✅ Graph saved for case {case_id}")
        
        return {
            'entities_saved': len(entities),
            'relationships_saved': len(relationships),
            'case_id': str(case_id),
            'institution_id': str(institution_id),
            'status': 'success',
        }

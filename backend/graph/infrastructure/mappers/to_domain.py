"""
Graph Infrastructure - ORM to Domain Mapper

Maps GraphEntity and GraphRelationship → GraphAggregate.
Anti-corruption layer between Persistence and Domain.
"""

from typing import List, Dict, Any
from uuid import UUID

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.models import GraphEntity, GraphRelationship
from backend.graph.infrastructure.interfaces.identity import IdentityGenerator


# backend/graph/infrastructure/mappers/to_domain.py

class OrmToGraphMapper:
    """
    ORM to Domain Mapper.
    
    CRITICAL: Must map persistence IDs back to business keys.
    """
    
    def __init__(self, factory):
        self._factory = factory
    
    def map(
        self,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> GraphAggregate:
        """Map ORM models to domain aggregate."""
        if not entities:
            raise ValueError("Cannot create aggregate from empty entities")
        
        # 1. Build entity_id → business_key mapping
        entity_to_business_key = {}
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if business_key:
                entity_to_business_key[entity.id] = business_key
        
        # 2. Map entities → nodes
        nodes = self._map_nodes(entities)
        
        # 3. Map relationships → edges (using business keys)
        edges = self._map_edges(relationships, entity_to_business_key)
        
        # 4. Build aggregate via factory
        case_id = UUID(entities[0].case_id)
        institution_id = UUID(entities[0].institution_id)
        
        return self._factory.rehydrate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=nodes,
            edges=edges,
            version=1,  # TODO: Get from GraphMetadataRepository
            checksum="",  # TODO: Get from GraphMetadataRepository
        )
    
    def _map_nodes(self, entities: List[GraphEntity]) -> List[GraphNode]:
        """Map ORM entities to domain nodes."""
        nodes = []
        for entity in entities:
            business_key = entity.extra_data.get("business_key", entity.id)
            node = GraphNode(
                business_key=business_key,
                entity_type=entity.entity_type,
                name=entity.name,
                extra_data=entity.extra_data,
            )
            nodes.append(node)
        return nodes
    
    def _map_edges(
        self,
        relationships: List[GraphRelationship],
        entity_to_business_key: Dict[str, str],
    ) -> List[GraphEdge]:
        """
        Map ORM relationships to domain edges.
        
        CRITICAL: Converts persistence IDs back to business keys.
        """
        edges = []
        for rel in relationships:
            # Convert persistence IDs to business keys
            source_business_key = entity_to_business_key.get(rel.source_id)
            target_business_key = entity_to_business_key.get(rel.target_id)
            
            if source_business_key is None:
                raise ValueError(f"Source entity not found: {rel.source_id}")
            if target_business_key is None:
                raise ValueError(f"Target entity not found: {rel.target_id}")
            
            edge = GraphEdge(
                source_key=source_business_key,  # ← Business key, NOT persistence ID
                target_key=target_business_key,  # ← Business key, NOT persistence ID
                relationship_type=rel.relationship_type,
                weight=rel.weight,
                amount=rel.amount,
                description=rel.description,
                extra_data=rel.extra_data,
            )
            edges.append(edge)
        return edges
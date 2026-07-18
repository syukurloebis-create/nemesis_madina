"""
Graph Infrastructure - Domain to ORM Mapper

Maps GraphAggregate → GraphEntity and GraphRelationship.
Anti-corruption layer between Domain and Persistence.
"""

from typing import List, Dict, Any, Tuple
from uuid import uuid4

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.models import (
    GraphEntity,
    GraphRelationship,
)
from backend.graph.infrastructure.interfaces.identity import IdentityGenerator


class GraphToOrmMapper:
    """
    Domain to ORM Mapper - PURE, DETERMINISTIC.
    
    NO identity generation.
    IdentityGenerator is injected from outside.
    """
    
    def __init__(self):
        # No identity generator - pure mapper
        pass
    
    def map_entities(
        self,
        aggregate: GraphAggregate,
        entity_ids: Dict[str, str],  # business_key → persistence_id
    ) -> List[GraphEntity]:
        """Map entities with pre-generated IDs."""
        entities = []
        for node in aggregate.nodes:
            entity_id = entity_ids.get(node.business_key)
            if entity_id is None:
                raise ValueError(f"No ID for entity: {node.business_key}")
            
            entity = GraphEntity(
                id=entity_id,
                case_id=str(aggregate.case_id),
                institution_id=str(aggregate.institution_id),
                entity_type=node.entity_type,
                name=node.name,
                extra_data={
                    "business_key": node.business_key,
                    **node.extra_data,
                },
            )
            entities.append(entity)
        return entities
    
    def map_relationships(
        self,
        aggregate: GraphAggregate,
        entity_ids: Dict[str, str],
        relationship_ids: Dict[tuple, str],
    ) -> List[GraphRelationship]:
        """Map relationships with pre-generated IDs."""
        relationships = []
        for edge in aggregate.edges:
            source_id = entity_ids.get(edge.source_key)
            target_id = entity_ids.get(edge.target_key)
            
            if source_id is None:
                raise ValueError(f"Source not found: {edge.source_key}")
            if target_id is None:
                raise ValueError(f"Target not found: {edge.target_key}")
            
            rel_id = relationship_ids.get(
                (edge.source_key, edge.target_key, edge.relationship_type)
            )
            if rel_id is None:
                rel_id = str(uuid.uuid4())  # Generate new ID if needed
            
            relationship = GraphRelationship(
                id=rel_id,
                case_id=str(aggregate.case_id),
                institution_id=str(aggregate.institution_id),
                source_id=source_id,
                target_id=target_id,
                relationship_type=edge.relationship_type,
                weight=edge.weight,
                amount=edge.amount,
                description=edge.description,
                extra_data={
                    "source_business_key": edge.source_key,
                    "target_business_key": edge.target_key,
                    **edge.extra_data,
                },
            )
            relationships.append(relationship)
        return relationships
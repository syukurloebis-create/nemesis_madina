"""
Graph Invariant Validator.

Enforces all graph data invariants before persistence.
"""

from typing import List, Set, Tuple
from uuid import UUID

from backend.graph.models import GraphEntity, GraphRelationship


class GraphInvariantValidator:
    """
    Validates graph data invariants.
    
    Invariants enforced:
    1. GraphEntity MUST have case_id
    2. GraphEntity MUST have institution_id
    3. GraphEntity MUST have entity_type
    4. GraphEntity MUST have name
    5. GraphRelationship MUST have case_id
    6. GraphRelationship MUST have institution_id
    7. GraphRelationship MUST connect entities within same case
    8. Duplicate edges are prohibited
    9. Self-loops are prohibited
    10. No orphan relationships (source and target must exist)
    """
    
    @staticmethod
    def validate_entity(entity: GraphEntity) -> None:
        """Validate a single entity."""
        if entity.case_id is None:
            raise ValueError("GraphEntity MUST have case_id")
        if entity.institution_id is None:
            raise ValueError("GraphEntity MUST have institution_id")
        if not entity.entity_type:
            raise ValueError("GraphEntity MUST have entity_type")
        if not entity.name:
            raise ValueError("GraphEntity MUST have name")
    
    @staticmethod
    def validate_entities(entities: List[GraphEntity]) -> None:
        """Validate multiple entities."""
        for entity in entities:
            GraphInvariantValidator.validate_entity(entity)
    
    @staticmethod
    def validate_relationship(
        relationship: GraphRelationship,
        entities: List[GraphEntity],
    ) -> None:
        """Validate a single relationship."""
        if relationship.case_id is None:
            raise ValueError("GraphRelationship MUST have case_id")
        if relationship.institution_id is None:
            raise ValueError("GraphRelationship MUST have institution_id")
        if not relationship.source_id:
            raise ValueError("GraphRelationship MUST have source_id")
        if not relationship.target_id:
            raise ValueError("GraphRelationship MUST have target_id")
        if not relationship.relationship_type:
            raise ValueError("GraphRelationship MUST have relationship_type")
        
        # Check self-loop
        if relationship.source_id == relationship.target_id:
            raise ValueError(f"Self-loop is prohibited: {relationship.source_id} -> {relationship.target_id}")
        
        # Check source and target exist
        entity_ids = {e.id for e in entities}
        if relationship.source_id not in entity_ids:
            raise ValueError(f"Source entity {relationship.source_id} not found")
        if relationship.target_id not in entity_ids:
            raise ValueError(f"Target entity {relationship.target_id} not found")
        
        # Check same case
        source_case = next((e.case_id for e in entities if e.id == relationship.source_id), None)
        target_case = next((e.case_id for e in entities if e.id == relationship.target_id), None)
        if source_case != relationship.case_id or target_case != relationship.case_id:
            raise ValueError(
                f"Relationship MUST connect entities within the same case. "
                f"Source case: {source_case}, Target case: {target_case}, Relationship case: {relationship.case_id}"
            )
    
    @staticmethod
    def validate_relationships(
        relationships: List[GraphRelationship],
        entities: List[GraphEntity],
    ) -> None:
        """Validate multiple relationships."""
        for relationship in relationships:
            GraphInvariantValidator.validate_relationship(relationship, entities)
    
    @staticmethod
    def validate_no_duplicate_edges(
        relationships: List[GraphRelationship],
    ) -> None:
        """Check for duplicate edges."""
        seen: Set[Tuple[str, str, str]] = set()
        for rel in relationships:
            key = (rel.source_id, rel.target_id, rel.relationship_type)
            if key in seen:
                raise ValueError(f"Duplicate edge: {rel.source_id} -> {rel.target_id} ({rel.relationship_type})")
            seen.add(key)
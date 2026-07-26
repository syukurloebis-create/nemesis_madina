# backend/graph/infrastructure/orm_checksum.py (NEW FILE)

"""
Graph Infrastructure - ORM Checksum Adapter

Converts ORM models to canonical representation for checksum computation.
Used by Infrastructure layer only.
"""

from typing import List, Dict, Any
from backend.graph.models import GraphEntity, GraphRelationship
from backend.graph.domain.checksum import GraphChecksumService


class ORMChecksumAdapter:
    """
    Adapter for computing checksums from ORM models.
    Infrastructure layer - uses ORM models, not domain aggregates.
    """

    def __init__(self):
        self._service = GraphChecksumService()

    def compute_from_orm(
        self,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> str:
        """Compute checksum from ORM models."""
        canonical = self._to_canonical_from_orm(entities, relationships)
        canonical["_schema_version"] = self._service.SCHEMA_VERSION
        return self._service._compute_hash(canonical)

    def _to_canonical_from_orm(
        self,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> Dict[str, Any]:
        """Convert ORM models to canonical dict."""
        sorted_entities = sorted(entities, key=lambda e: e.extra_data.get("business_key", ""))
        sorted_relationships = sorted(
            relationships,
            key=lambda r: (r.source_id, r.target_id)
        )

        return {
            "entities": [
                {
                    "business_key": e.extra_data.get("business_key"),
                    "entity_type": e.entity_type,
                    "name": e.name,
                }
                for e in sorted_entities
            ],
            "relationships": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "relationship_type": r.relationship_type,
                    "weight": r.weight,
                    "amount": r.amount,
                }
                for r in sorted_relationships
            ],
        }
"""
Graph Domain - Checksum Service

Single source of truth for checksum computation.
Used by Domain, Infrastructure, Audit, Export, Replication.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.models import GraphEntity, GraphRelationship


class GraphChecksumService:
    """
    Single source of truth for checksum computation.

    Used by:
    - Domain (for aggregate validation)
    - Infrastructure (for persistence checksum)
    - Audit (for integrity verification)
    - Export/Replication (for consistency checks)

    DEPRECATED: This is a skeleton. Use CanonicalChecksumService in infrastructure.
    """
    
    SCHEMA_VERSION = 1

    def compute_from_aggregate(self, aggregate: GraphAggregate) -> str:
        """Compute checksum from aggregate (Domain use)."""
        canonical = self._to_canonical(aggregate)
        canonical["_schema_version"] = self.SCHEMA_VERSION
        return self._compute_hash(canonical)

    def compute_from_orm(
        self,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> str:
        """Compute checksum from ORM models (Infrastructure use)."""
        canonical = self._to_canonical_from_orm(entities, relationships)
        canonical["_schema_version"] = self.SCHEMA_VERSION
        return self._compute_hash(canonical)

    def _to_canonical(self, aggregate: GraphAggregate) -> Dict[str, Any]:
        """Convert aggregate to canonical dict."""
        sorted_nodes = sorted(aggregate.nodes, key=lambda n: n.business_key)
        sorted_edges = sorted(
            aggregate.edges,
            key=lambda e: (e.source_key, e.target_key, e.relationship_type)
        )

        return {
            "case_id": str(aggregate.case_id),
            "institution_id": str(aggregate.institution_id),
            "nodes": [
                {
                    "business_key": n.business_key,
                    "entity_type": n.entity_type,
                    "name": n.name,
                }
                for n in sorted_nodes
            ],
            "edges": [
                {
                    "source_key": e.source_key,
                    "target_key": e.target_key,
                    "relationship_type": e.relationship_type,
                    "weight": e.weight,
                    "amount": e.amount,
                }
                for e in sorted_edges
            ],
        }

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

    def _compute_hash(self, canonical: Dict[str, Any]) -> str:
        """Compute SHA-256 hash from canonical representation."""
        json_str = json.dumps(canonical, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
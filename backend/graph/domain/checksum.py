# backend/graph/domain/checksum.py

"""
Graph Domain - Checksum Service

Pure domain logic for checksum computation.
No ORM dependencies.
"""

import hashlib
import json
from typing import Dict, Any, List

from backend.graph.domain.aggregate import GraphAggregate


class GraphChecksumService:
    """
    Single source of truth for checksum computation.
    """

    SCHEMA_VERSION = 1

    def compute(self, aggregate: GraphAggregate) -> str:
        """
        Backward-compatible API.

        Legacy callers and unit tests still invoke `compute()`.
        The canonical implementation is `compute_from_aggregate()`.
        """
        return self.compute_from_aggregate(aggregate)

    def compute_from_aggregate(
        self,
        aggregate: GraphAggregate,
    ) -> str:        
        canonical = self._to_canonical(aggregate)
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

    def _compute_hash(self, canonical: Dict[str, Any]) -> str:
        """Compute SHA-256 hash from canonical representation."""
        json_str = json.dumps(canonical, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
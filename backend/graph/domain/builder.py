"""
Graph Domain - Domain Builder
"""

from dataclasses import dataclass
from typing import List
from uuid import UUID

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.factory import GraphAggregateFactory


@dataclass
class DomainBuildResult:
    """Result of domain build operation."""
    
    aggregate: GraphAggregate
    nodes_count: int
    edges_count: int
    duplicates_removed: int


class GraphDomainBuilder:
    """Graph Domain Builder - Domain Service."""
    
    def __init__(
        self,
        factory: GraphAggregateFactory,
        duplicate_mode: str = "repair",
    ):
        self._factory = factory
        self._duplicate_mode = duplicate_mode
    
    def build_from_nodes_and_edges(
        self,
        case_id: UUID,
        institution_id: UUID,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
    ) -> DomainBuildResult:
        """Build aggregate from nodes and edges."""
        # Deduplicate
        unique_nodes, dup_nodes = self._deduplicate_nodes(nodes)
        unique_edges, dup_edges = self._deduplicate_edges(edges)
        
        # Create aggregate via factory
        aggregate = self._factory.create(
            case_id=case_id,
            institution_id=institution_id,
            nodes=unique_nodes,
            edges=unique_edges,
        )
        
        return DomainBuildResult(
            aggregate=aggregate,
            nodes_count=len(unique_nodes),
            edges_count=len(unique_edges),
            duplicates_removed=dup_nodes + dup_edges,
        )
    
    def _deduplicate_nodes(self, nodes: List[GraphNode]) -> tuple:
        """Deduplicate nodes by business_key."""
        seen = {}
        duplicates = 0
        for node in nodes:
            if node.business_key in seen:
                duplicates += 1
                if self._duplicate_mode == "strict":
                    raise ValueError(f"Duplicate node: {node.business_key}")
            else:
                seen[node.business_key] = node
        return list(seen.values()), duplicates
    
    def _deduplicate_edges(self, edges: List[GraphEdge]) -> tuple:
        """Deduplicate edges by key."""
        seen = {}
        duplicates = 0
        for edge in edges:
            key = (edge.source_key, edge.target_key, edge.relationship_type)
            if key in seen:
                duplicates += 1
                if self._duplicate_mode == "strict":
                    raise ValueError(f"Duplicate edge: {key}")
            else:
                seen[key] = edge
        return list(seen.values()), duplicates


# ✅ Ensure DomainBuildResult is exported
__all__ = [
    "DomainBuildResult",
    "GraphDomainBuilder",
]
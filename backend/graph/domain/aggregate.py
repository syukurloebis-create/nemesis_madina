"""
Graph Domain - Aggregate Root

Immutable aggregate representing a complete graph for a case.
Protects business invariants.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import (
    Tuple,
    List,
    Dict,
    Any,
    Set,
    Optional,
    Mapping,         
)
from types import MappingProxyType   
from uuid import UUID
from datetime import datetime, timezone

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge


class BusinessInvariantViolation(Exception):
    """Raised when a business invariant is violated."""
    pass


@dataclass(frozen=True)
class GraphAggregate:
    case_id: UUID
    institution_id: UUID
    nodes: Tuple[GraphNode, ...]
    edges: Tuple[GraphEdge, ...]
    version: int = 1
    checksum: Optional[str] = None 
    
    # Cached indices (computed lazily)
    _node_index: Mapping[str, GraphNode] = field(default_factory=dict, repr=False)
    _edge_index: Mapping[Tuple[str, str, str], GraphEdge] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Build indices and validate invariants."""
        if self.checksum is not None and not self.checksum:
            raise ValueError("checksum must be None or non-empty string")

        # Build indices as read-only MappingProxyType
        node_index = {n.business_key: n for n in self.nodes}
        edge_index = {}
        for edge in self.edges:
            key = (edge.source_key, edge.target_key, edge.relationship_type)
            edge_index[key] = edge
        
        object.__setattr__(self, '_node_index', MappingProxyType(node_index))
        object.__setattr__(self, '_edge_index', MappingProxyType(edge_index))
        
        # Validate invariants
        self._validate_no_duplicate_nodes()
        self._validate_no_duplicate_edges()
        self._validate_no_orphan_edges()
        self._validate_no_self_loops()
    
    def contains_node(self, business_key: str) -> bool:
        """O(1) lookup."""
        return business_key in self._node_index
    
    def get_node_by_key(self, business_key: str) -> Optional[GraphNode]:
        """O(1) lookup."""
        return self._node_index.get(business_key)
    
    def contains_edge(self, source_key: str, target_key: str, relationship_type: str) -> bool:
        """O(1) lookup."""
        key = (source_key, target_key, relationship_type)
        return key in self._edge_index
    
    def with_checksum(self, checksum: str) -> 'GraphAggregate':
        """Return new aggregate with checksum."""
        return GraphAggregate(
            case_id=self.case_id,
            institution_id=self.institution_id,
            nodes=self.nodes,
            edges=self.edges,
            version=self.version,
            checksum=checksum,
        )
    
    # ============================================================
    # BUSINESS INVARIANTS
    # ============================================================
    
    def _validate_no_duplicate_nodes(self) -> None:
        """Invariant: No duplicate business keys."""
        seen = set()
        for node in self.nodes:
            if node.business_key in seen:
                raise BusinessInvariantViolation(
                    f"Duplicate node: {node.business_key}"
                )
            seen.add(node.business_key)
    
    def _validate_no_duplicate_edges(self) -> None:
        """Invariant: No duplicate edges."""
        seen = set()
        for edge in self.edges:
            key = (edge.source_key, edge.target_key, edge.relationship_type)
            if key in seen:
                raise BusinessInvariantViolation(
                    f"Duplicate edge: {edge.source_key} -> {edge.target_key}"
                )
            seen.add(key)
    
    def _validate_no_orphan_edges(self) -> None:
        """Invariant: All edges reference existing nodes."""
        node_keys = {n.business_key for n in self.nodes}
        for edge in self.edges:
            if edge.source_key not in node_keys:
                raise BusinessInvariantViolation(
                    f"Orphan edge source: {edge.source_key}"
                )
            if edge.target_key not in node_keys:
                raise BusinessInvariantViolation(
                    f"Orphan edge target: {edge.target_key}"
                )
    
    def _validate_no_self_loops(self) -> None:
        """Invariant: No self-loops."""
        for edge in self.edges:
            if edge.source_key == edge.target_key:
                raise BusinessInvariantViolation(
                    f"Self-loop: {edge.source_key} -> {edge.target_key}"
                )
    
    # ============================================================
    # QUERY OPERATIONS
    # ============================================================
    
    @property
    def node_count(self) -> int:
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        return len(self.edges)
    
    def contains_node(self, business_key: str) -> bool:
        """Check if node exists."""
        for node in self.nodes:
            if node.business_key == business_key:
                return True
        return False
    
    def contains_edge(self, source_key: str, target_key: str, relationship_type: str) -> bool:
        """Check if edge exists."""
        for edge in self.edges:
            if edge.source_key == source_key and edge.target_key == target_key and edge.relationship_type == relationship_type:
                return True
        return False
    
    def get_node_by_key(self, business_key: str) -> Optional[GraphNode]:
        """Get node by business key."""
        for node in self.nodes:
            if node.business_key == business_key:
                return node
        return None
    
    def get_edges_from(self, source_key: str) -> Tuple[GraphEdge, ...]:
        """Get all edges from a source node."""
        return tuple(e for e in self.edges if e.source_key == source_key)
    
    def get_edges_to(self, target_key: str) -> Tuple[GraphEdge, ...]:
        """Get all edges to a target node."""
        return tuple(e for e in self.edges if e.target_key == target_key)
    
    def compute_statistics(self) -> GraphStatistics:
        """Compute graph statistics."""
        if self.node_count < 2:
            density = 0.0
        else:
            max_edges = self.node_count * (self.node_count - 1) / 2
            density = self.edge_count / max_edges if max_edges > 0 else 0.0
        
        if self.node_count == 0:
            avg_degree = 0.0
            max_degree = 0
            min_degree = 0
        else:
            degrees = {}
            for edge in self.edges:
                degrees[edge.source_key] = degrees.get(edge.source_key, 0) + 1
                degrees[edge.target_key] = degrees.get(edge.target_key, 0) + 1
            avg_degree = (2 * self.edge_count) / self.node_count
            max_degree = max(degrees.values()) if degrees else 0
            min_degree = min(degrees.values()) if degrees else 0
        
        return GraphStatistics(
            node_count=self.node_count,
            edge_count=self.edge_count,
            density=density,
            avg_degree=avg_degree,
            max_degree=max_degree,
            min_degree=min_degree,
        )
    
    # ============================================================
    # MUTATION OPERATIONS (Return new aggregates)
    # ============================================================
    
    def add_node(self, node: GraphNode) -> 'GraphAggregate':
        """Return new aggregate with node added."""
        if self.contains_node(node.business_key):
            raise BusinessInvariantViolation(
                f"Node already exists: {node.business_key}"
            )
        new_nodes = list(self.nodes) + [node]
        return GraphAggregate(
            case_id=self.case_id,
            institution_id=self.institution_id,
            nodes=tuple(new_nodes),
            edges=self.edges,
            version=self.version + 1,
        )
    
    def add_edge(self, edge: GraphEdge) -> 'GraphAggregate':
        """Return new aggregate with edge added."""
        if self.contains_edge(edge.source_key, edge.target_key, edge.relationship_type):
            raise BusinessInvariantViolation(
                f"Edge already exists: {edge.source_key} -> {edge.target_key}"
            )
        if not self.contains_node(edge.source_key):
            raise BusinessInvariantViolation(
                f"Source node not found: {edge.source_key}"
            )
        if not self.contains_node(edge.target_key):
            raise BusinessInvariantViolation(
                f"Target node not found: {edge.target_key}"
            )
        new_edges = list(self.edges) + [edge]
        return GraphAggregate(
            case_id=self.case_id,
            institution_id=self.institution_id,
            nodes=self.nodes,
            edges=tuple(new_edges),
            version=self.version + 1,
        )
    
    def remove_node(self, business_key: str) -> 'GraphAggregate':
        """Return new aggregate with node removed."""
        if not self.contains_node(business_key):
            raise BusinessInvariantViolation(
                f"Node not found: {business_key}"
            )
        new_nodes = [n for n in self.nodes if n.business_key != business_key]
        new_edges = [
            e for e in self.edges
            if e.source_key != business_key and e.target_key != business_key
        ]
        return GraphAggregate(
            case_id=self.case_id,
            institution_id=self.institution_id,
            nodes=tuple(new_nodes),
            edges=tuple(new_edges),
            version=self.version + 1,
        )
    
    # ============================================================
    # SERIALIZATION
    # ============================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "case_id": str(self.case_id),
            "institution_id": str(self.institution_id),
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "version": self.version,
            "statistics": self.compute_statistics().to_dict(),
        }

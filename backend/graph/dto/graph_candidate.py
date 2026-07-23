"""
Graph Candidate — Pure Domain DTO.

NO persistence, NO UUID, NO SQL.
Immutable dataclass with frozen=True.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class GraphNode:
    """
    Pure graph node — NO persistence details.
    
    Attributes:
        name: Node identifier (e.g., vendor name, person name)
        node_type: Type of node (vendor, person, institution, etc.)
        external_id: Optional external identifier for merge across builders
        properties: Domain-specific properties (no persistence)
        confidence: Node confidence score (0.0 - 1.0)
        risk_score: Node risk score (0.0 - 100.0)
    """
    name: str
    node_type: str
    external_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    risk_score: float = 0.0


@dataclass(frozen=True)
class GraphEdge:
    """
    Pure graph edge — NO persistence details.
    
    Attributes:
        source: Source node name
        target: Target node name
        relationship_type: Type of relationship
        weight: Edge weight (0.0 - 1.0)
        properties: Domain-specific properties (no persistence)
    """
    source: str
    target: str
    relationship_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphCandidate:
    """
    Pure graph structure — NO persistence details.
    
    Attributes:
        nodes: List of graph nodes
        edges: List of graph edges
        metadata: Pipeline metadata (builder_id, version, generated_at, statistics)
    """
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def node_count(self) -> int:
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        return len(self.edges)
    
    @property
    def is_empty(self) -> bool:
        return len(self.nodes) == 0
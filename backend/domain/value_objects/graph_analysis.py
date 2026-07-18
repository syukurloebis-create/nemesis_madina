# backend/domain/value_objects/graph_analysis.py
"""
NEMESIS Madina - Graph Analysis Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable fields
"""

from dataclasses import dataclass, field
from typing import Optional, Sequence, List, Dict, Any


@dataclass(frozen=True)
class GraphAnalysis:
    """Graph analysis result - Pure Value Object."""

    # Core fields (required)
    case_id: str = ""
    nodes: Sequence[dict] = field(default_factory=list)
    edges: Sequence[dict] = field(default_factory=list)
    
    # Additional fields (with defaults)
    cluster_count: int = 0
    max_cluster_size: int = 0
    density: float = 0.0
    diameter: int = 0
    avg_path_length: float = 0.0
    has_cycles: bool = False
    complexity_score: float = 0.0
    
    # Application layer fields
    entities: List[Any] = field(default_factory=list)
    relationships: List[Any] = field(default_factory=list)
    engine_status: str = "UNKNOWN"

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def is_connected(self) -> bool:
        """Check if graph is connected."""
        return self.density > 0.0
"""
Graph Domain - Statistics

Domain statistics DTO.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class GraphStatistics:
    """
    Graph Statistics - Domain DTO.
    
    Computed statistics for a graph aggregate.
    """
    
    node_count: int
    edge_count: int
    density: float
    avg_degree: float
    max_degree: int
    min_degree: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "density": round(self.density, 4),
            "avg_degree": round(self.avg_degree, 2),
            "max_degree": self.max_degree,
            "min_degree": self.min_degree,
        }


class GraphStatisticsService:
    """
    Graph Statistics Service - Domain Service.
    
    Computes statistics from aggregate.
    Separate from aggregate for SRP.
    """
    
    def compute(self, aggregate: GraphAggregate) -> GraphStatistics:
        """Compute statistics from aggregate."""
        if aggregate.node_count < 2:
            density = 0.0
        else:
            max_edges = aggregate.node_count * (aggregate.node_count - 1) / 2
            density = aggregate.edge_count / max_edges if max_edges > 0 else 0.0
        
        if aggregate.node_count == 0:
            avg_degree = 0.0
            max_degree = 0
            min_degree = 0
        else:
            degrees = {}
            for edge in aggregate.edges:
                degrees[edge.source_key] = degrees.get(edge.source_key, 0) + 1
                degrees[edge.target_key] = degrees.get(edge.target_key, 0) + 1
            avg_degree = (2 * aggregate.edge_count) / aggregate.node_count
            max_degree = max(degrees.values()) if degrees else 0
            min_degree = min(degrees.values()) if degrees else 0
        
        return GraphStatistics(
            node_count=aggregate.node_count,
            edge_count=aggregate.edge_count,
            density=density,
            avg_degree=avg_degree,
            max_degree=max_degree,
            min_degree=min_degree,
        )

# GraphAggregate no longer has compute_statistics()
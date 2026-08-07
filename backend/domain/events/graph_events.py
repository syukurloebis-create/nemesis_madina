# backend/domain/events/graph_events.py
"""
NEMESIS Madina - Graph Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.case_id import CaseId


@dataclass(frozen=True)
class GraphPayload:
    """New-style payload for graph events."""
    
    case_id: CaseId
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    cluster_count: int
    max_cluster_size: int
    density: float
    diameter: int
    avg_path_length: float
    has_cycles: bool
    complexity_score: float
    status: str = "SUCCESS"
    entities: tuple = () 
    relationships: tuple = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "nodes": self.nodes,
            "edges": self.edges,
            "cluster_count": self.cluster_count,
            "max_cluster_size": self.max_cluster_size,
            "density": self.density,
            "diameter": self.diameter,
            "avg_path_length": self.avg_path_length,
            "has_cycles": self.has_cycles,
            "complexity_score": self.complexity_score,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphPayload":
        return cls(
            case_id=CaseId(data["case_id"]),
            nodes=data["nodes"],
            edges=data["edges"],
            cluster_count=data["cluster_count"],
            max_cluster_size=data["max_cluster_size"],
            density=data["density"],
            diameter=data["diameter"],
            avg_path_length=data["avg_path_length"],
            has_cycles=data["has_cycles"],
            complexity_score=data["complexity_score"],
            status=data.get("status", "SUCCESS"),
        )


@dataclass(frozen=True)
class GraphAnalysisCompleted(DomainEvent[GraphPayload]):
    EVENT_NAME = "GraphAnalysisCompleted"
    EVENT_VERSION = "1"


# ============================================================================
# COMPATIBILITY ADAPTER (Plain Class)
# ============================================================================

class GraphAnalysisPerformed(GraphAnalysisCompleted):
    """Compatibility adapter for old aggregate calls."""
    
    def __init__(self, case_id: CaseId, analysis: GraphAnalysis):
        payload = GraphPayload(
            case_id=case_id,
            nodes=analysis.nodes,
            edges=analysis.edges,
            cluster_count=analysis.cluster_count,
            max_cluster_size=analysis.max_cluster_size,
            density=analysis.density,
            diameter=analysis.diameter,
            avg_path_length=analysis.avg_path_length,
            has_cycles=analysis.has_cycles,
            complexity_score=analysis.complexity_score,
        )
        super().__init__(payload=payload)
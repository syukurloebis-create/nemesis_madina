# backend/infrastructure/mappers/graph_mapper.py
"""
NEMESIS Madina - Graph Analysis Mapper
✅ Maps GraphAnalysis Value Object ↔ JSONB
✅ Stateless, pure functions
"""

from typing import Optional, Dict, Any
from backend.domain.value_objects.graph_analysis import GraphAnalysis


class GraphAnalysisMapper:
    """Graph Analysis mapper for DDD infrastructure."""

    @staticmethod
    def to_dict(analysis: Optional[GraphAnalysis]) -> Optional[Dict[str, Any]]:
        """Convert domain object to JSONB data."""
        if analysis is None:
            return None
        
        return {
            "case_id": analysis.case_id,
            "nodes": analysis.nodes,
            "edges": analysis.edges,
            "cluster_count": analysis.cluster_count,
            "max_cluster_size": analysis.max_cluster_size,
            "density": analysis.density,
            "diameter": analysis.diameter,
            "avg_path_length": analysis.avg_path_length,
            "has_cycles": analysis.has_cycles,
            "complexity_score": analysis.complexity_score,
            "entities": analysis.entities,
            "relationships": analysis.relationships,
            "engine_status": analysis.engine_status,
        }

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional[GraphAnalysis]:
        """Convert JSONB data to domain object."""
        if data is None:
            return None
        
        return GraphAnalysis(
            case_id=data.get("case_id", ""),
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            cluster_count=data.get("cluster_count", 0),
            max_cluster_size=data.get("max_cluster_size", 0),
            density=float(data.get("density", 0.0)),
            diameter=data.get("diameter", 0),
            avg_path_length=float(data.get("avg_path_length", 0.0)),
            has_cycles=data.get("has_cycles", False),
            complexity_score=float(data.get("complexity_score", 0.0)),
            entities=data.get("entities", []),
            relationships=data.get("relationships", []),
            engine_status=data.get("engine_status", "UNKNOWN"),
        )
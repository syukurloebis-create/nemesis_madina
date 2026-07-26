# backend/graph/__init__.py

"""
Graph Module - Backend
"""

from backend.graph.models import (
    GraphEntity,
    GraphRelationship,
    CollusionDetection,
    NodeType,
    EdgeType
)
from backend.graph.builder import GraphBuilder, Graph
from backend.graph.service import GraphIntelligenceService
from backend.graph.relationship_graph import RelationshipGraph
from backend.graph.metrics import GraphMetrics
from backend.graph.routes import router
from backend.graph.collusion_detector import CollusionDetector

from backend.graph.intelligence.collusion_detector import (
    CollusionDetector as IntelligenceCollusionDetector,
)
from backend.graph.intelligence.temporal_graph import TemporalGraph, temporal_graph
from backend.graph.intelligence.centrality import CentralityAnalyzer, centrality_analyzer
from backend.graph.intelligence.pattern_mining import PatternMiner, pattern_miner

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.types import NodeType as DomainNodeType, EdgeType as DomainEdgeType


__all__ = [
    # ORM Models
    "GraphEntity",
    "GraphRelationship",
    "CollusionDetection",
    # Builders
    "GraphBuilder",
    "Graph",
    # Services
    "GraphIntelligenceService",
    "RelationshipGraph",
    "GraphMetrics",
    "router",
    # Intelligence
    "TemporalGraph",
    "temporal_graph",
    "CollusionDetector",           
    "IntelligenceCollusionDetector",  
    "CentralityAnalyzer",
    "centrality_analyzer",
    "PatternMiner",
    "pattern_miner",
    # Domain
    "GraphNode",
    "GraphEdge",
    "GraphAggregate",
    "NodeType",
    "EdgeType",
]
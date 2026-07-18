"""
Collusion Detector
Mendeteksi pola collusion dalam graph
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import combinations
import logging
import uuid

# Import temporal_graph dari file yang sama
from .temporal_graph import temporal_graph, TemporalGraph, TemporalEdge

logger = logging.getLogger(__name__)


@dataclass
class CollusionPattern:
    """Collusion pattern detected"""
    pattern_id: str
    type: str
    confidence: float
    actors: List[str]
    evidence: List[Dict[str, Any]]
    temporal_range: Tuple[datetime, datetime]
    score: float
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "type": self.type,
            "confidence": self.confidence,
            "actors": self.actors,
            "evidence": self.evidence,
            "temporal_range": {
                "start": self.temporal_range[0].isoformat(),
                "end": self.temporal_range[1].isoformat()
            },
            "score": self.score,
            "description": self.description,
            "metadata": self.metadata
        }


class CollusionDetector:
    """
    Collusion Detection Engine
    Mendeteksi berbagai pola collusion
    """

    def __init__(self, graph: Optional[TemporalGraph] = None):
        self.graph = graph or temporal_graph
        self.patterns: List[CollusionPattern] = []

    def detect_all(self) -> List[CollusionPattern]:
        """Run all collusion detection algorithms"""
        self.patterns = []

        # 1. Triangle detection
        triangles = self._detect_triangles()
        self.patterns.extend(triangles)

        # 2. Bidirectional detection
        bidirectional = self._detect_bidirectional()
        self.patterns.extend(bidirectional)

        # 3. Temporal pattern detection
        temporal = self._detect_temporal_patterns()
        self.patterns.extend(temporal)

        # 4. Community overlap
        community = self._detect_community_overlap()
        self.patterns.extend(community)

        # 5. Centrality anomaly
        centrality = self._detect_centrality_anomaly()
        self.patterns.extend(centrality)

        # Sort by score
        self.patterns.sort(key=lambda x: x.score, reverse=True)

        return self.patterns

    def _get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        neighbors = set()
        for target, _ in self.graph.adjacency.get(node_id, []):
            neighbors.add(target)
        for source, _ in self.graph.reverse_adjacency.get(node_id, []):
            neighbors.add(source)
        return list(neighbors)

    def _get_edges_between(self, node1: str, node2: str) -> List[Dict[str, Any]]:
        """Get edges between two nodes"""
        edges = []
        for edge in self.graph.edges.values():
            if (edge.source == node1 and edge.target == node2) or \
               (edge.source == node2 and edge.target == node1):
                edges.append({
                    "id": edge.id,
                    "type": edge.type,
                    "created_at": edge.created_at,
                    "confidence": edge.confidence
                })
        return edges

    def _detect_triangles(self) -> List[CollusionPattern]:
        """Detect triangle patterns"""
        patterns = []
        nodes = list(self.graph.nodes.keys())

        for i, node1 in enumerate(nodes):
            neighbors1 = self._get_neighbors(node1)
            for j, node2 in enumerate(nodes[i+1:], i+1):
                if node2 not in neighbors1:
                    continue
                neighbors2 = self._get_neighbors(node2)
                common = set(neighbors1) & set(neighbors2)
                common.discard(node1)
                common.discard(node2)

                for common_node in common:
                    edges1 = self._get_edges_between(node1, common_node)
                    edges2 = self._get_edges_between(node2, common_node)
                    edges3 = self._get_edges_between(node1, node2)

                    if edges1 and edges2 and edges3:
                        all_times = [e["created_at"] for e in edges1 + edges2 + edges3]
                        time_range = max(all_times) - min(all_times)
                        temporal_score = 1 - min(time_range.days / 30, 1)

                        score = (min((len(edges1) + len(edges2) + len(edges3)) / 3, 1) * 0.6 + temporal_score * 0.4)

                        if score > 0.5:
                            patterns.append(CollusionPattern(
                                pattern_id=f"triangle_{node1}_{node2}_{common_node}",
                                type="triangle",
                                confidence=score,
                                actors=[node1, node2, common_node],
                                evidence=[{
                                    "type": "triangle",
                                    "description": f"Triangle relationship between {node1}, {node2}, and {common_node}",
                                    "nodes": [node1, node2, common_node]
                                }],
                                temporal_range=(min(all_times), max(all_times)),
                                score=score * 100,
                                description=f"Triangle collusion pattern between {node1}, {node2}, and {common_node}"
                            ))

        return patterns

    def _detect_bidirectional(self) -> List[CollusionPattern]:
        """Detect bidirectional relationships"""
        patterns = []
        seen = set()

        for source, targets in self.graph.adjacency.items():
            for target, _ in targets:
                if (source, target) in seen:
                    continue
                seen.add((source, target))

                reverse_edges = self._get_edges_between(target, source)
                if reverse_edges:
                    forward_edges = self._get_edges_between(source, target)
                    all_times = [e["created_at"] for e in forward_edges + reverse_edges]
                    time_range = max(all_times) - min(all_times)
                    temporal_score = 1 - min(time_range.days / 30, 1)
                    score = (min((len(forward_edges) + len(reverse_edges)) / 4, 1) * 0.5 + temporal_score * 0.5)

                    if score > 0.6:
                        patterns.append(CollusionPattern(
                            pattern_id=f"bidirectional_{source}_{target}",
                            type="bidirectional",
                            confidence=score,
                            actors=[source, target],
                            evidence=[{
                                "type": "bidirectional",
                                "description": f"Bidirectional relationship between {source} and {target}",
                                "nodes": [source, target]
                            }],
                            temporal_range=(min(all_times), max(all_times)),
                            score=score * 100,
                            description=f"Bidirectional relationship between {source} and {target}"
                        ))

        return patterns

    def _detect_temporal_patterns(self) -> List[CollusionPattern]:
        """Detect suspicious temporal patterns"""
        patterns = []
        now = datetime.now()
        start_time = now - timedelta(days=30)

        for node_id, node in self.graph.nodes.items():
            timeline = self.graph.get_activity_timeline(node_id, start_time, now, interval="day")

            if len(timeline) >= 5:
                values = list(timeline.values())
                avg = sum(values) / len(values)
                max_val = max(values)

                if max_val > avg * 3:
                    patterns.append(CollusionPattern(
                        pattern_id=f"burst_{node_id}",
                        type="activity_burst",
                        confidence=0.7,
                        actors=[node_id],
                        evidence=[{
                            "type": "activity_burst",
                            "description": f"Activity burst detected for {node.label}",
                            "details": {"max_activity": max_val, "avg_activity": avg}
                        }],
                        temporal_range=(start_time, now),
                        score=70,
                        description=f"Suspicious activity burst for {node.label}"
                    ))

        return patterns

    def _detect_community_overlap(self) -> List[CollusionPattern]:
        """Detect overlapping communities"""
        patterns = []
        nodes = list(self.graph.nodes.keys())
        communities = []

        for node in nodes:
            neighbors = self._get_neighbors(node)
            if len(neighbors) >= 3:
                communities.append(set([node] + neighbors))

        for i, comm1 in enumerate(communities):
            for comm2 in communities[i+1:]:
                overlap = comm1 & comm2
                if len(overlap) >= 2:
                    score = len(overlap) / min(len(comm1), len(comm2))
                    if score > 0.5:
                        patterns.append(CollusionPattern(
                            pattern_id=f"overlap_{i}_{i+1}",
                            type="community_overlap",
                            confidence=score,
                            actors=list(overlap),
                            evidence=[{
                                "type": "community_overlap",
                                "description": f"Community overlap detected",
                                "details": {"overlap_size": len(overlap)}
                            }],
                            temporal_range=(datetime.now() - timedelta(days=30), datetime.now()),
                            score=score * 100,
                            description=f"Community overlap detected with {len(overlap)} actors"
                        ))

        return patterns

    def _detect_centrality_anomaly(self) -> List[CollusionPattern]:
        """Detect centrality anomalies"""
        patterns = []
        degrees = {}

        for node in self.graph.nodes:
            degrees[node] = self.graph.get_node_degree(node)

        if degrees:
            avg_degree = sum(degrees.values()) / len(degrees)
            std_degree = (sum((d - avg_degree) ** 2 for d in degrees.values()) / len(degrees)) ** 0.5

            for node, degree in degrees.items():
                if degree > avg_degree + 2 * std_degree:
                    patterns.append(CollusionPattern(
                        pattern_id=f"centrality_{node}",
                        type="centrality_anomaly",
                        confidence=0.8,
                        actors=[node],
                        evidence=[{
                            "type": "centrality_anomaly",
                            "description": f"Node has abnormally high centrality",
                            "details": {"degree": degree, "avg_degree": avg_degree}
                        }],
                        temporal_range=(datetime.now() - timedelta(days=30), datetime.now()),
                        score=min(degree / (avg_degree + std_degree) * 50, 100),
                        description=f"High centrality anomaly detected for {node}"
                    ))

        return patterns

    def get_patterns_by_type(self, pattern_type: str) -> List[CollusionPattern]:
        """Get patterns by type"""
        return [p for p in self.patterns if p.type == pattern_type]

    def get_high_confidence_patterns(self, threshold: float = 0.7) -> List[CollusionPattern]:
        """Get patterns with confidence above threshold"""
        return [p for p in self.patterns if p.confidence >= threshold]

    def get_summary(self) -> Dict[str, Any]:
        """Get collusion detection summary"""
        return {
            "total_patterns": len(self.patterns),
            "by_type": {t: len(self.get_patterns_by_type(t))
                       for t in set(p.type for p in self.patterns)},
            "high_confidence": len(self.get_high_confidence_patterns()),
            "avg_confidence": sum(p.confidence for p in self.patterns) / len(self.patterns) if self.patterns else 0,
            "top_patterns": [p.to_dict() for p in self.patterns[:5]]
        }


# Singleton instance
collusion_detector = CollusionDetector()
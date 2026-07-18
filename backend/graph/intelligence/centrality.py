"""
Actor Centrality Analysis
Menghitung berbagai metrik centrality
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .temporal_graph import temporal_graph, TemporalGraph

logger = logging.getLogger(__name__)


@dataclass
class CentralityMetrics:
    """Centrality metrics for an actor"""
    node_id: str
    degree: float
    betweenness: float
    closeness: float
    eigenvector: float
    pagerank: float
    combined_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "degree": self.degree,
            "betweenness": self.betweenness,
            "closeness": self.closeness,
            "eigenvector": self.eigenvector,
            "pagerank": self.pagerank,
            "combined_score": self.combined_score
        }


class CentralityAnalyzer:
    """
    Centrality Analysis Engine
    Menghitung berbagai metrik centrality
    """

    def __init__(self, graph: Optional[TemporalGraph] = None):
        self.graph = graph or temporal_graph

    def analyze_all(self) -> Dict[str, CentralityMetrics]:
        """Calculate all centrality metrics"""
        results = {}

        # Calculate metrics
        degree = self.calculate_degree()
        betweenness = self.calculate_betweenness()
        closeness = self.calculate_closeness()
        eigenvector = self.calculate_eigenvector()
        pagerank = self.calculate_pagerank()

        # Combine
        all_nodes = set(degree.keys()) | set(betweenness.keys()) | \
                    set(closeness.keys()) | set(eigenvector.keys()) | \
                    set(pagerank.keys())

        for node_id in all_nodes:
            combined = self._calculate_combined(
                degree.get(node_id, 0),
                betweenness.get(node_id, 0),
                closeness.get(node_id, 0),
                eigenvector.get(node_id, 0),
                pagerank.get(node_id, 0)
            )

            results[node_id] = CentralityMetrics(
                node_id=node_id,
                degree=degree.get(node_id, 0),
                betweenness=betweenness.get(node_id, 0),
                closeness=closeness.get(node_id, 0),
                eigenvector=eigenvector.get(node_id, 0),
                pagerank=pagerank.get(node_id, 0),
                combined_score=combined
            )

        return results

    def calculate_degree(self) -> Dict[str, float]:
        """Calculate degree centrality"""
        degrees = {}

        for node_id in self.graph.nodes:
            degree = self.graph.get_node_degree(node_id) if hasattr(self.graph, 'get_node_degree') else len(self._get_neighbors(node_id))
            degrees[node_id] = degree

        # Normalize
        max_degree = max(degrees.values()) if degrees else 1
        return {k: v / max_degree for k, v in degrees.items()}

    def calculate_betweenness(self) -> Dict[str, float]:
        """Calculate betweenness centrality"""
        betweenness = defaultdict(float)
        nodes = list(self.graph.nodes.keys())

        for i, source in enumerate(nodes):
            for target in nodes[i+1:]:
                paths = self._find_shortest_paths(source, target)
                if not paths:
                    continue

                # Count occurrences
                for path in paths:
                    for node in path[1:-1]:
                        betweenness[node] += 1 / len(paths)

        # Normalize
        max_betweenness = max(betweenness.values()) if betweenness else 1
        return {k: v / max_betweenness for k, v in betweenness.items()}

    def calculate_closeness(self) -> Dict[str, float]:
        """Calculate closeness centrality"""
        closeness = {}

        for node_id in self.graph.nodes:
            distances = self._get_distances(node_id)
            if distances:
                total_distance = sum(distances.values())
                closeness[node_id] = len(distances) / total_distance if total_distance > 0 else 0

        # Normalize
        max_closeness = max(closeness.values()) if closeness else 1
        return {k: v / max_closeness for k, v in closeness.items()}

    def calculate_eigenvector(self) -> Dict[str, float]:
        """Calculate eigenvector centrality (simplified)"""
        # Simplified implementation using iterative method
        scores = {node_id: 1.0 for node_id in self.graph.nodes}

        for _ in range(50):
            new_scores = defaultdict(float)

            for node_id in self.graph.nodes:
                neighbors = self._get_neighbors(node_id)
                for neighbor in neighbors:
                    new_scores[node_id] += scores.get(neighbor, 0)

            # Normalize
            max_score = max(new_scores.values()) if new_scores else 1
            if max_score > 0:
                new_scores = {k: v / max_score for k, v in new_scores.items()}

            scores = new_scores

        # Normalize to 0-1
        max_score = max(scores.values()) if scores else 1
        return {k: v / max_score for k, v in scores.items()}

    def calculate_pagerank(self) -> Dict[str, float]:
        """Calculate PageRank centrality"""
        nodes = list(self.graph.nodes.keys())
        n = len(nodes)

        if n == 0:
            return {}

        # Initialize scores
        scores = {node_id: 1.0 / n for node_id in nodes}
        damping = 0.85

        for _ in range(50):
            new_scores = defaultdict(float)

            for node_id in nodes:
                # Calculate contribution from outgoing edges
                outgoing = self._get_outgoing_neighbors(node_id)
                if outgoing:
                    contribution = scores[node_id] / len(outgoing)
                    for target in outgoing:
                        new_scores[target] += contribution

            # Apply damping
            for node_id in nodes:
                new_scores[node_id] = damping * new_scores[node_id] + (1 - damping) / n

            scores = new_scores

        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}

        return scores

    def _get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        neighbors = set()

        if hasattr(self.graph, 'adjacency'):
            for target, _ in self.graph.adjacency.get(node_id, []):
                neighbors.add(target)
            for source, _ in self.graph.reverse_adjacency.get(node_id, []):
                neighbors.add(source)
        else:
            # Fallback for non-temporal graph
            for edge in self.graph.edges.values():
                if edge.source == node_id:
                    neighbors.add(edge.target)
                if edge.target == node_id:
                    neighbors.add(edge.source)

        return list(neighbors)

    def _get_outgoing_neighbors(self, node_id: str) -> List[str]:
        """Get outgoing neighbors"""
        if hasattr(self.graph, 'adjacency'):
            return [target for target, _ in self.graph.adjacency.get(node_id, [])]
        return []

    def _find_shortest_paths(self, source: str, target: str) -> List[List[str]]:
        """Find all shortest paths between source and target"""
        if source == target:
            return [[source]]

        visited = {source: 0}
        queue = [(source, [source])]
        paths = []
        min_distance = None

        while queue:
            current, path = queue.pop(0)

            if min_distance and len(path) > min_distance:
                break

            for neighbor in self._get_neighbors(current):
                if neighbor == target:
                    if min_distance is None:
                        min_distance = len(path)
                    if len(path) <= min_distance:
                        paths.append(path + [neighbor])
                elif neighbor not in visited or visited[neighbor] >= len(path):
                    visited[neighbor] = len(path)
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def _get_distances(self, source: str) -> Dict[str, int]:
        """Get distances from source to all nodes"""
        distances = {source: 0}
        queue = [(source, 0)]

        while queue:
            current, dist = queue.pop(0)
            for neighbor in self._get_neighbors(current):
                if neighbor not in distances:
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))

        return distances

    def _calculate_combined(
        self,
        degree: float,
        betweenness: float,
        closeness: float,
        eigenvector: float,
        pagerank: float
    ) -> float:
        """Calculate combined centrality score"""
        weights = {
            'degree': 0.25,
            'betweenness': 0.25,
            'closeness': 0.20,
            'eigenvector': 0.15,
            'pagerank': 0.15
        }

        return (
            degree * weights['degree'] +
            betweenness * weights['betweenness'] +
            closeness * weights['closeness'] +
            eigenvector * weights['eigenvector'] +
            pagerank * weights['pagerank']
        )

    def get_top_actors(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get top n actors by combined centrality"""
        metrics = self.analyze_all()
        sorted_actors = sorted(
            metrics.items(),
            key=lambda x: x[1].combined_score,
            reverse=True
        )
        return [
            {
                "node_id": node_id,
                "metrics": metrics.to_dict()
            }
            for node_id, metrics in sorted_actors[:n]
        ]


# Singleton instance
centrality_analyzer = CentralityAnalyzer()
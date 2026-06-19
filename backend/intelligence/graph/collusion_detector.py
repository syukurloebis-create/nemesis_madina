"""
Collusion Detector - Graph Intelligence Layer

Uses RelationshipGraph methods that ACTUALLY EXIST.
No assumptions about missing methods (clustering_coefficient, betweenness).
"""

import warnings
from typing import List, Dict, Any

warnings.warn(
    "This module uses legacy graph interface. Consider migrating to backend.graph.intelligence.services.collusion_detector",
    DeprecationWarning,
    stacklevel=2
)

# SAFE IMPORT - now available after __init__.py fix
try:
    from backend.graph import RelationshipGraph, GraphMetrics
except ImportError:
    # Fallback for backward compatibility
    from backend.graph.relationship_graph import RelationshipGraph
    from backend.graph.metrics import GraphMetrics


class CollusionDetector:
    """
    Graph-based collusion detection using ONLY available methods:
    - get_degree() or degrees dict
    - get_all_nodes() or nodes property
    - get_edge_count() or edges
    """

    def __init__(self, graph: RelationshipGraph):
        self.graph = graph
        self._metrics = GraphMetrics(graph) if graph else None

    def _get_degree_safe(self, node_id: str) -> int:
        """Safely get node degree from graph"""
        try:
            # Try property first
            if hasattr(self.graph, 'degrees'):
                return self.graph.degrees.get(node_id, 0)
            # Try method
            if hasattr(self.graph, 'get_degree'):
                return self.graph.get_degree(node_id)
            # Fallback: count edges manually
            if hasattr(self.graph, 'edges'):
                return sum(1 for e in self.graph.edges if e.source == node_id or e.target == node_id)
        except Exception:
            pass
        return 0

    def _get_nodes_safe(self) -> List[str]:
        """Safely get all node IDs from graph"""
        try:
            if hasattr(self.graph, 'get_all_nodes'):
                return self.graph.get_all_nodes()
            if hasattr(self.graph, 'nodes'):
                if callable(self.graph.nodes):
                    return self.graph.nodes()
                return list(self.graph.nodes)
        except Exception:
            pass
        return []

    def _get_edge_count_safe(self) -> int:
        """Safely get total edge count"""
        try:
            if hasattr(self.graph, 'get_edge_count'):
                return self.graph.get_edge_count()
            if hasattr(self.graph, 'edges'):
                return len(self.graph.edges)
        except Exception:
            pass
        return 0

    def compute_node_score(self, node_id: str) -> float:
        """
        Collusion score based on graph signals.
        Uses degree centrality as primary signal (always available).
        """
        degree = self._get_degree_safe(node_id)
        
        # Normalize degree by max possible (use edge count as proxy)
        edge_count = max(self._get_edge_count_safe(), 1)
        max_degree = min(edge_count, 100)
        
        normalized_degree = min(degree / max(max_degree, 1), 1.0)
        
        # Simplified score - only degree centrality (reliable)
        score = normalized_degree * 0.7
        
        # Add small boost if metrics available
        if self._metrics:
            try:
                density = self._metrics.get_density() if hasattr(self._metrics, 'get_density') else 0
                score += density * 0.3
            except Exception:
                pass
        
        return round(min(score, 1.0), 4)

    def detect(self, threshold: float = 0.65) -> List[Dict[str, Any]]:
        """
        Detect collusion clusters.
        
        Returns list of suspicious nodes with scores.
        """
        suspicious_nodes = []
        
        try:
            nodes = self._get_nodes_safe()
            
            if not nodes:
                return []
            
            for node in nodes:
                score = self.compute_node_score(node)
                
                if score >= threshold:
                    suspicious_nodes.append({
                        "node": node,
                        "score": score,
                        "degree": self._get_degree_safe(node)
                    })
            
            # Sort by score descending
            suspicious_nodes.sort(key=lambda x: x["score"], reverse=True)
            
        except Exception as e:
            # Silent fail - don't crash the pipeline
            warnings.warn(f"Collusion detection failed: {e}")
            return []
        
        return suspicious_nodes

    def get_summary(self) -> Dict[str, Any]:
        """Get detection summary statistics"""
        nodes = self._get_nodes_safe()
        edge_count = self._get_edge_count_safe()
        
        return {
            "total_nodes": len(nodes),
            "total_edges": edge_count,
            "graph_has_data": len(nodes) > 0 and edge_count > 0,
            "detector_ready": self.graph is not None
        }


# Preserve original exports
__all__ = [
    "RelationshipGraph",
    "CollusionDetector",
    "GraphMetrics"
]
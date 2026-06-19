"""
Collusion Detector - Detect collusion patterns in graph
"""

from typing import List, Set, Tuple, Dict, Any
from collections import defaultdict
from backend.graph.models import Graph


class CollusionDetector:
    """Detect collusion patterns in relationship graphs"""
    
    def __init__(self, graph: Graph, config: Dict[str, Any] = None):
        self.graph = graph
        self.config = config or {
            "min_edges": 3,
            "min_weight": 0.5,
            "anomaly_threshold": 0.7,
            "triangle_weight": 0.4,
            "hub_weight": 0.3,
            "density_weight": 0.3
        }
    
    def detect_triangles(self) -> List[Tuple[str, str, str]]:
        """Detect triangles (3-node cycles) - potential collusion"""
        triangles = []
        nodes = list(self.graph.nodes.keys())
        
        for i, a in enumerate(nodes):
            neighbors = set(self.graph.get_neighbors(a))
            
            for j in range(i + 1, len(nodes)):
                b = nodes[j]
                if b not in neighbors:
                    continue
                
                # Find common neighbors
                b_neighbors = set(self.graph.get_neighbors(b))
                common = neighbors & b_neighbors
                
                for c in common:
                    if c != a and c != b:
                        triangles.append((a, b, c))
        
        return triangles
    
    def detect_high_degree_nodes(self, threshold: int = 10) -> List[Tuple[str, int]]:
        """Detect nodes with high degree (potential hubs)"""
        high_degree = []
        
        for node_id in self.graph.nodes:
            degree = self.graph.get_degree(node_id)
            if degree >= threshold:
                high_degree.append((node_id, degree))
        
        return sorted(high_degree, key=lambda x: x[1], reverse=True)
    
    def detect_dense_subgraphs(self, min_nodes: int = 3) -> List[Set[str]]:
        """Detect dense subgraphs using simple heuristic"""
        components = self._find_connected_components()
        dense_subgraphs = []
        
        for component in components:
            if len(component) < min_nodes:
                continue
            
            # Calculate edge density within component
            edge_count = self._count_edges_in_component(component)
            max_possible = len(component) * (len(component) - 1)
            density = (2 * edge_count) / max_possible if max_possible > 0 else 0
            
            if density > 0.5:  # Dense subgraph threshold
                dense_subgraphs.append(component)
        
        return dense_subgraphs
    
    def compute_collusion_score(self) -> Dict[str, Any]:
        """Compute overall collusion risk score"""
        triangles = self.detect_triangles()
        high_degree = self.detect_high_degree_nodes(5)
        dense_subgraphs = self.detect_dense_subgraphs(3)
        
        # Score calculation
        triangle_score = min(len(triangles) / 100, 1.0)
        hub_score = min(len(high_degree) / 20, 1.0)
        density_score = min(len(dense_subgraphs) / 10, 1.0)
        
        overall_score = (
            triangle_score * self.config["triangle_weight"] +
            hub_score * self.config["hub_weight"] +
            density_score * self.config["density_weight"]
        )
        
        severity = "HIGH" if overall_score > 0.7 else "MEDIUM" if overall_score > 0.3 else "LOW"
        
        return {
            "score": round(overall_score, 3),
            "severity": severity,
            "triangle_count": len(triangles),
            "hub_count": len(high_degree),
            "dense_subgraph_count": len(dense_subgraphs),
            "details": {
                "top_hubs": high_degree[:5],
                "triangle_count": len(triangles),
                "density_score": density_score
            }
        }
    
    def _find_connected_components(self) -> List[Set[str]]:
        """Find connected components in the graph"""
        visited = set()
        components = []
        
        for node_id in self.graph.nodes:
            if node_id not in visited:
                component = self._bfs_component(node_id)
                components.append(component)
                visited.update(component)
        
        return components
    
    def _bfs_component(self, start: str) -> Set[str]:
        """BFS to find connected component"""
        from collections import deque
        visited = {start}
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            for neighbor in self.graph.get_neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return visited
    
    def _count_edges_in_component(self, component: Set[str]) -> int:
        """Count edges within a component"""
        count = 0
        for edge in self.graph.edges:
            if edge.source in component and edge.target in component:
                count += 1
        return count
    
    def generate_report(self) -> str:
        """Generate collusion detection report"""
        score_data = self.compute_collusion_score()
        
        report = []
        report.append("=" * 60)
        report.append("COLLUSION DETECTION REPORT")
        report.append("=" * 60)
        report.append(f"Overall Collusion Score: {score_data['score']}")
        report.append(f"Severity: {score_data['severity']}")
        report.append("")
        report.append("METRICS:")
        report.append(f"  - Triangles detected: {score_data['triangle_count']}")
        report.append(f"  - High-degree nodes: {score_data['hub_count']}")
        report.append(f"  - Dense subgraphs: {score_data['dense_subgraph_count']}")
        
        if score_data['details']['top_hubs']:
            report.append("")
            report.append("TOP HUBS:")
            for node_id, degree in score_data['details']['top_hubs'][:5]:
                report.append(f"  - {node_id}: degree {degree}")
        
        return "\n".join(report)
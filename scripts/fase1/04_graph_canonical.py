#!/usr/bin/env python3
"""
NEMESIS FASE 1 - Graph Domain Canonicalization
Menggabungkan duplicate graph modules
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

GRAPH_DIR = PROJECT_ROOT / "backend" / "graph"

# Files yang akan digabung
DUPLICATE_SOURCES = {
    "relationship_graph": [
        "backend/intelligence/graph/relationship_graph.py",
        "backend/intelligence/core/graph/relationship_graph.py",
    ],
    "collusion_detector": [
        "backend/intelligence/graph/collusion_detector.py",
        "backend/intelligence/core/graph/collusion_detector.py",
    ]
}

def create_graph_directory():
    """Buat struktur direktori graph"""
    print("\n📁 Creating graph directory structure...")
    
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buat __init__.py
    init_file = GRAPH_DIR / "__init__.py"
    init_content = '''"""
NEMESIS Graph Domain - Single Source of Truth
==============================================
Modul ini adalah canonical source untuk graph operations.

Exports:
    - RelationshipGraph: Core graph structure
    - CollusionDetector: Collusion detection algorithms
    - QueryBuilder: Graph query builder
    - GraphMetrics: Graph metrics computation
"""

from backend.graph.relationship_graph import RelationshipGraph
from backend.graph.collusion_detector import CollusionDetector
from backend.graph.query_builder import QueryBuilder
from backend.graph.metrics import GraphMetrics

__all__ = [
    'RelationshipGraph',
    'CollusionDetector', 
    'QueryBuilder',
    'GraphMetrics'
]
'''
    init_file.write_text(init_content)
    print(f"  ✅ Created: {init_file}")
    return True

def create_relationship_graph():
    """Buat unified relationship_graph.py"""
    content = '''"""
Relationship Graph - Core Graph Structure for Entity Relationships
"""

from typing import Dict, Set, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class GraphNode:
    """Node in relationship graph"""
    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge in relationship graph"""
    source: str
    target: str
    label: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)


class RelationshipGraph:
    """Directed weighted graph for entity relationships"""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
        self._reverse_adjacency: Dict[str, List[Tuple[str, str, float]]] = defaultdict(list)
    
    def add_node(self, node_id: str, label: str, **properties) -> GraphNode:
        """Add or update node"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.properties.update(properties)
        else:
            node = GraphNode(id=node_id, label=label, properties=properties)
            self.nodes[node_id] = node
        return node
    
    def add_edge(self, source: str, target: str, label: str, weight: float = 1.0, **properties) -> Optional[GraphEdge]:
        """Add edge between nodes"""
        if source not in self.nodes or target not in self.nodes:
            return None
        
        edge = GraphEdge(
            source=source,
            target=target,
            label=label,
            weight=weight,
            properties=properties
        )
        self.edges.append(edge)
        self._adjacency[source].append((target, label, weight))
        self._reverse_adjacency[target].append((source, label, weight))
        return edge
    
    def get_neighbors(self, node_id: str, direction: str = "out") -> List[Tuple[str, str, float]]:
        """Get neighbors of a node"""
        if direction == "out":
            return self._adjacency.get(node_id, [])
        elif direction == "in":
            return self._reverse_adjacency.get(node_id, [])
        else:  # both
            out = self._adjacency.get(node_id, [])
            inc = self._reverse_adjacency.get(node_id, [])
            return list(set(out + inc))
    
    def get_degree(self, node_id: str) -> int:
        """Get degree of node"""
        return len(self._adjacency.get(node_id, [])) + len(self._reverse_adjacency.get(node_id, []))
    
    def get_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find shortest path using BFS"""
        if source not in self.nodes or target not in self.nodes:
            return None
        
        from collections import deque
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            node, path = queue.popleft()
            
            if node == target:
                return path
            
            for neighbor, _, _ in self._adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_connected_components(self) -> List[Set[str]]:
        """Find connected components"""
        visited = set()
        components = []
        
        for node_id in self.nodes:
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
            for neighbor, _, _ in self.get_neighbors(node, "both"):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return visited
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get graph metrics"""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "density": (2 * len(self.edges)) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0,
            "components": len(self.get_connected_components()),
            "avg_degree": sum(self.get_degree(n) for n in self.nodes) / len(self.nodes) if self.nodes else 0
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary"""
        return {
            "nodes": [
                {"id": nid, "label": node.label, "properties": node.properties}
                for nid, node in self.nodes.items()
            ],
            "edges": [
                {"source": e.source, "target": e.target, "label": e.label, "weight": e.weight}
                for e in self.edges
            ],
            "metrics": self.get_metrics()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> "RelationshipGraph":
        """Import graph from dictionary"""
        graph = RelationshipGraph()
        
        for node_data in data.get("nodes", []):
            graph.add_node(node_data["id"], node_data["label"], **node_data.get("properties", {}))
        
        for edge_data in data.get("edges", []):
            graph.add_edge(
                edge_data["source"],
                edge_data["target"],
                edge_data["label"],
                edge_data.get("weight", 1.0)
            )
        
        return graph
    
    def clear(self):
        """Clear all nodes and edges"""
        self.nodes.clear()
        self.edges.clear()
        self._adjacency.clear()
        self._reverse_adjacency.clear()
'''
    
    file_path = GRAPH_DIR / "relationship_graph.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_collusion_detector():
    """Buat unified collusion_detector.py"""
    content = '''"""
Collusion Detector - Detect collusion patterns in relationship graph
"""

from typing import Dict, List, Set, Tuple, Any, Optional
from collections import defaultdict
from backend.graph.relationship_graph import RelationshipGraph


class CollusionDetector:
    """Detect collusion patterns in entity relationships"""
    
    def __init__(self, graph: RelationshipGraph):
        self.graph = graph
    
    def detect_triangles(self) -> List[Tuple[str, str, str]]:
        """Detect triangles (3-node cycles) - potential collusion"""
        triangles = []
        nodes = list(self.graph.nodes.keys())
        
        for i, a in enumerate(nodes):
            neighbors = set(n for n, _, _ in self.graph.get_neighbors(a, "both"))
            
            for j in range(i + 1, len(nodes)):
                b = nodes[j]
                if b not in neighbors:
                    continue
                
                for k in range(j + 1, len(nodes)):
                    c = nodes[k]
                    if c in neighbors and c in self.graph.get_neighbors(b, "both"):
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
        components = self.graph.get_connected_components()
        dense_subgraphs = []
        
        for component in components:
            if len(component) < min_nodes:
                continue
            
            # Calculate edge density within component
            subgraph_nodes = {n: True for n in component}
            edge_count = 0
            
            for edge in self.graph.edges:
                if edge.source in subgraph_nodes and edge.target in subgraph_nodes:
                    edge_count += 1
            
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
        
        overall_score = (triangle_score * 0.4 + hub_score * 0.3 + density_score * 0.3)
        
        return {
            "score": round(overall_score, 3),
            "triangle_count": len(triangles),
            "high_degree_nodes": len(high_degree),
            "dense_subgraphs": len(dense_subgraphs),
            "severity": "HIGH" if overall_score > 0.7 else "MEDIUM" if overall_score > 0.3 else "LOW",
            "details": {
                "triangles": triangles[:10],  # Limit for output
                "high_degree": high_degree[:10],
                "dense_subgraphs": [list(sg) for sg in dense_subgraphs[:5]]
            }
        }
    
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
        report.append(f"  - High-degree nodes: {score_data['high_degree_nodes']}")
        report.append(f"  - Dense subgraphs: {score_data['dense_subgraphs']}")
        
        return "\\n".join(report)
'''
    
    file_path = GRAPH_DIR / "collusion_detector.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_query_builder():
    """Buat query_builder.py - graph queries"""
    content = '''"""
Query Builder - Build complex graph queries
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from backend.graph.relationship_graph import RelationshipGraph


class QueryBuilder:
    """Build and execute graph queries"""
    
    def __init__(self, graph: RelationshipGraph):
        self.graph = graph
    
    def find_paths(self, source: str, target: str, max_depth: int = 3) -> List[List[str]]:
        """Find all paths between nodes up to max_depth"""
        if source not in self.graph.nodes or target not in self.graph.nodes:
            return []
        
        paths = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            if current == target and len(path) > 1:
                paths.append(path.copy())
                return
            
            for neighbor, _, _ in self.graph.get_neighbors(current, "out"):
                if neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, path, depth + 1)
                    path.pop()
        
        dfs(source, [source], 0)
        return paths
    
    def find_common_neighbors(self, node1: str, node2: str) -> List[str]:
        """Find common neighbors between two nodes"""
        neighbors1 = set(n for n, _, _ in self.graph.get_neighbors(node1, "both"))
        neighbors2 = set(n for n, _, _ in self.graph.get_neighbors(node2, "both"))
        return list(neighbors1 & neighbors2)
    
    def get_subgraph(self, node_ids: Set[str]) -> RelationshipGraph:
        """Extract subgraph containing specified nodes"""
        subgraph = RelationshipGraph()
        
        for node_id in node_ids:
            if node_id in self.graph.nodes:
                node = self.graph.nodes[node_id]
                subgraph.add_node(node_id, node.label, **node.properties)
        
        for edge in self.graph.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph.add_edge(edge.source, edge.target, edge.label, edge.weight, **edge.properties)
        
        return subgraph
    
    def get_ego_graph(self, node_id: str, radius: int = 1) -> RelationshipGraph:
        """Get ego graph (neighborhood) around node"""
        ego_nodes = {node_id}
        current_level = {node_id}
        
        for _ in range(radius):
            next_level = set()
            for n in current_level:
                for neighbor, _, _ in self.graph.get_neighbors(n, "both"):
                    ego_nodes.add(neighbor)
                    next_level.add(neighbor)
            current_level = next_level
        
        return self.get_subgraph(ego_nodes)
    
    def find_nodes_by_label(self, label: str) -> List[str]:
        """Find nodes with specific label"""
        return [nid for nid, node in self.graph.nodes.items() if node.label == label]
    
    def find_nodes_by_property(self, key: str, value: Any) -> List[str]:
        """Find nodes with specific property value"""
        result = []
        for nid, node in self.graph.nodes.items():
            if node.properties.get(key) == value:
                result.append(nid)
        return result
'''
    
    file_path = GRAPH_DIR / "query_builder.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_metrics():
    """Buat metrics.py - graph metrics"""
    content = '''"""
Graph Metrics - Compute graph statistics
"""

from typing import Dict, Any, List
from backend.graph.relationship_graph import RelationshipGraph


class GraphMetrics:
    """Compute various graph metrics"""
    
    def __init__(self, graph: RelationshipGraph):
        self.graph = graph
    
    def compute_degree_distribution(self) -> Dict[int, int]:
        """Compute degree distribution"""
        distribution = {}
        for node_id in self.graph.nodes:
            degree = self.graph.get_degree(node_id)
            distribution[degree] = distribution.get(degree, 0) + 1
        return distribution
    
    def compute_clustering_coefficient(self) -> float:
        """Compute average clustering coefficient"""
        if len(self.graph.nodes) < 3:
            return 0.0
        
        total = 0.0
        for node_id in self.graph.nodes:
            neighbors = [n for n, _, _ in self.graph.get_neighbors(node_id, "both")]
            if len(neighbors) < 2:
                continue
            
            # Count edges between neighbors
            edge_count = 0
            neighbor_set = set(neighbors)
            for edge in self.graph.edges:
                if edge.source in neighbor_set and edge.target in neighbor_set:
                    edge_count += 1
            
            max_possible = len(neighbors) * (len(neighbors) - 1) / 2
            if max_possible > 0:
                total += edge_count / max_possible
        
        return total / len(self.graph.nodes)
    
    def compute_diameter(self) -> int:
        """Compute graph diameter (longest shortest path)"""
        if len(self.graph.nodes) < 2:
            return 0
        
        max_distance = 0
        nodes = list(self.graph.nodes.keys())
        
        for i, source in enumerate(nodes):
            # BFS from source
            distances = {source: 0}
            from collections import deque
            queue = deque([source])
            
            while queue:
                current = queue.popleft()
                for neighbor, _, _ in self.graph.get_neighbors(current, "out"):
                    if neighbor not in distances:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)
            
            max_distance = max(max_distance, max(distances.values()))
        
        return max_distance
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive graph summary"""
        metrics = self.graph.get_metrics()
        metrics.update({
            "diameter": self.compute_diameter(),
            "clustering_coefficient": round(self.compute_clustering_coefficient(), 3),
            "degree_distribution": self.compute_degree_distribution()
        })
        return metrics
'''
    
    file_path = GRAPH_DIR / "metrics.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_deprecated_stubs():
    """Buat stub untuk duplicate files"""
    print("\n📝 Creating deprecated stubs...")
    
    deprecated_paths = [
        "backend/intelligence/graph/relationship_graph.py",
        "backend/intelligence/core/graph/relationship_graph.py",
        "backend/intelligence/graph/collusion_detector.py",
        "backend/intelligence/core/graph/collusion_detector.py",
    ]
    
    stub_content = '''# DEPRECATED - Use backend.graph instead
import warnings
warnings.warn(
    "This module is deprecated. Use 'from backend.graph import ...'",
    DeprecationWarning,
    stacklevel=2
)

from backend.graph import *

__all__ = [
    'RelationshipGraph',
    'CollusionDetector',
    'QueryBuilder',
    'GraphMetrics'
]
'''
    
    for path_str in deprecated_paths:
        file_path = PROJECT_ROOT / path_str
        if file_path.exists():
            file_path.write_text(stub_content)
            print(f"  ✅ Created stub: {file_path}")
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 1: GRAPH CANONICALIZATION")
    print("="*60)
    
    success = True
    success &= create_graph_directory()
    success &= create_relationship_graph()
    success &= create_collusion_detector()
    success &= create_query_builder()
    success &= create_metrics()
    
    create_deprecated_stubs()
    
    print("\n" + "="*60)
    if success:
        print("✅ GRAPH CANONICALIZATION COMPLETE")
        print(f"   Location: {GRAPH_DIR}")
        print("")
        print("   Merged duplicate modules:")
        print("     - relationship_graph.py (2 sources)")
        print("     - collusion_detector.py (2 sources)")
    else:
        print("❌ GRAPH CANONICALIZATION FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
"""
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

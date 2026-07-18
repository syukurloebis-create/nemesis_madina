"""Graph Builder - handles graph construction and manipulation"""

from typing import Dict, List, Any, Optional
from backend.graph.models import GraphEntity, GraphRelationship
from backend.graph.metrics import GraphMetrics


class Graph:
    """Simple in-memory graph representation"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
    
    def add_node(self, node_id: str, node_type: str, label: str, **kwargs) -> Dict:
        """Add a node to the graph"""
        self.nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            **kwargs
        }
        return self.nodes[node_id]
    
    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0, **kwargs) -> Dict:
        """Add an edge to the graph"""
        edge = {
            "source": source,
            "target": target,
            "type": edge_type,
            "weight": weight,
            **kwargs
        }
        self.edges.append(edge)
        return edge
    
    def get_neighbors(self, node_id: str) -> List[str]:
        """Get neighbors of a node"""
        neighbors = []
        for edge in self.edges:
            if edge["source"] == node_id:
                neighbors.append(edge["target"])
            elif edge["target"] == node_id:
                neighbors.append(edge["source"])
        return neighbors
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by id"""
        return self.nodes.get(node_id)
    
    def get_edge_count(self) -> int:
        """Get number of edges"""
        return len(self.edges)
    
    def get_node_count(self) -> int:
        """Get number of nodes"""
        return len(self.nodes)


class GraphBuilder:
    """Builder for creating and managing graphs"""
    
    def __init__(self):
        self._graph = Graph()
    
    def get_graph(self) -> Graph:
        """Get the current graph"""
        return self._graph
    
    def add_node(self, node_id: str, node_type, label: str, **kwargs) -> Dict:
        """Add a node to the graph"""
        node_type_str = node_type.value if hasattr(node_type, 'value') else str(node_type)
        return self._graph.add_node(node_id, node_type_str, label, **kwargs)
    
    def add_edge(self, source: str, target: str, edge_type, weight: float = 1.0, **kwargs) -> Optional[Dict]:
        """Add an edge to the graph"""
        if source not in self._graph.nodes or target not in self._graph.nodes:
            return None
        edge_type_str = edge_type.value if hasattr(edge_type, 'value') else str(edge_type)
        return self._graph.add_edge(source, target, edge_type_str, weight, **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get graph metrics"""
        return GraphMetrics(self._graph).get_summary()

"""Graph Metrics - calculate and summarize graph statistics"""

from typing import Dict, Any, List


class GraphMetrics:
    """Metrics calculator for graphs"""
    
    def __init__(self, graph):
        self.graph = graph
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary metrics"""
        nodes = self.graph.nodes
        edges = self.graph.edges
        
        # Count node types
        node_types = {}
        for node_id, node_data in nodes.items():
            node_type = node_data.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Count edge types
        edge_types = {}
        for edge in edges:
            edge_type = edge.get("type", "unknown")
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        return {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": node_types,
            "edge_types": edge_types
        }
    
    def get_collusion_summary(self) -> Dict[str, Any]:
        """Get collusion-specific metrics"""
        edges = self.graph.edges
        collusion_edges = [e for e in edges if e.get("type") == "collusion"]
        
        return {
            "collusion_edges": len(collusion_edges),
            "total_edges": len(edges),
            "collusion_percentage": round(len(collusion_edges) / max(len(edges), 1) * 100, 1)
        }

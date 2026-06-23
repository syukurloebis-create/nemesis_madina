"""
Query Builder - Build complex graph queries
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from graph.relationship_graph import RelationshipGraph


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

"""
Graph Builder — Entity to Graph Mapper
"""

from typing import List, Dict, Any, Set
from collections import defaultdict
import re


class GraphBuilder:
    
    def __init__(self):
        self.graph = defaultdict(set)
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []
    
    def add_node(self, node_id: str, node_type: str, name: str, **attrs) -> None:
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "name": name,
                "attributes": attrs,
            }
    
    def add_edge(self, source: str, target: str, edge_type: str = "transfer", **props) -> None:
        self.graph[source].add(target)
        self.edges.append({
            "source": source,
            "target": target,
            "type": edge_type,
            "properties": props,
        })
    
    def build_from_case_data(self, entities: List[Dict], transactions: List[Dict], ownerships: List[Dict] = None) -> "GraphBuilder":
        for entity in entities:
            node_id = self._normalize_id(entity.get("name", ""))
            if node_id:
                self.add_node(node_id, entity.get("type", "unknown"), entity.get("name", ""))
        
        for tx in transactions:
            from_node = self._normalize_id(tx.get("from", ""))
            to_node = self._normalize_id(tx.get("to", ""))
            if from_node and to_node and from_node != to_node:
                self.add_edge(from_node, to_node, "financial_transfer", amount=tx.get("amount", 0))
        
        return self
    
    def _normalize_id(self, name: str) -> str:
        if not name:
            return ""
        return re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
    
    def find_triangles(self) -> List[Dict[str, Any]]:
        triangles = []
        for start in list(self.graph.keys()):
            cycles = self._find_cycles(start, 3)
            for cycle in cycles:
                if len(cycle) == 4 and cycle[0] == cycle[-1]:
                    nodes = cycle[:-1]
                    names = [self.nodes.get(n, {}).get("name", n) for n in nodes]
                    if len(names) == 3:
                        triangles.append({
                            "type": "financial_triangle",
                            "entities": names,
                            "cycle": " → ".join(names) + f" → {names[0]}",
                            "confidence": 0.85,
                            "severity": 0.7,
                        })
        return triangles
    
    def _find_cycles(self, start: str, max_depth: int) -> List[List[str]]:
        cycles = []
        def dfs(current: str, path: List[str], depth: int):
            if depth > max_depth:
                return
            for neighbor in self.graph.get(current, []):
                if neighbor == start and depth >= 2:
                    cycles.append(path + [neighbor])
                elif neighbor not in path and depth < max_depth:
                    dfs(neighbor, path + [neighbor], depth + 1)
        dfs(start, [start], 0)
        return cycles
    
    def calculate_collusion_risk(self) -> float:
        triangles = self.find_triangles()
        if not triangles:
            return 0.0
        return round(len(triangles) * 25, 2)
    
    def get_graph_summary(self) -> Dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "triangle_count": len(self.find_triangles()),
            "collusion_risk": self.calculate_collusion_risk(),
        }

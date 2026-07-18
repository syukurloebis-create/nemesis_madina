"""
Knowledge Graph Builder
Membangun dan mengelola knowledge graph dari berbagai sumber
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeNode:
    """Node dalam knowledge graph"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeEdge:
    """Edge dalam knowledge graph"""
    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraph:
    """Knowledge graph untuk intelligence"""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[str]] = defaultdict(list)

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> KnowledgeNode:
        """Add node to graph"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.label = label
            node.type = node_type
            if properties:
                node.properties.update(properties)
            node.confidence = confidence
            node.updated_at = datetime.now()
            return node

        node = KnowledgeNode(
            id=node_id,
            label=label,
            type=node_type,
            properties=properties or {},
            confidence=confidence
        )
        self.nodes[node_id] = node
        logger.debug(f"Node added: {label} ({node_id})")
        return node

    def add_edge(
        self,
        edge_id: str,
        source: str,
        target: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0
    ) -> KnowledgeEdge:
        """Add edge to graph"""
        if source not in self.nodes:
            raise ValueError(f"Source node {source} not found")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} not found")

        edge = KnowledgeEdge(
            id=edge_id,
            source=source,
            target=target,
            type=edge_type,
            properties=properties or {},
            confidence=confidence
        )
        self.edges[edge_id] = edge
        self.adjacency[source].append(target)
        self.reverse_adjacency[target].append(source)
        logger.debug(f"Edge added: {source} -> {target} ({edge_type})")
        return edge

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get node by ID"""
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[KnowledgeEdge]:
        """Get edge by ID"""
        return self.edges.get(edge_id)

    def get_neighbors(self, node_id: str) -> List[KnowledgeNode]:
        """Get neighbors of a node"""
        neighbors = []
        for target in self.adjacency.get(node_id, []):
            if target in self.nodes:
                neighbors.append(self.nodes[target])
        for source in self.reverse_adjacency.get(node_id, []):
            if source in self.nodes:
                neighbors.append(self.nodes[source])
        return neighbors

    def get_edges_between(self, node1: str, node2: str) -> List[KnowledgeEdge]:
        """Get edges between two nodes"""
        return [
            e for e in self.edges.values()
            if (e.source == node1 and e.target == node2) or
               (e.source == node2 and e.target == node1)
        ]

    def get_nodes_by_type(self, node_type: str) -> List[KnowledgeNode]:
        """Get nodes by type"""
        return [n for n in self.nodes.values() if n.type == node_type]

    def get_edges_by_type(self, edge_type: str) -> List[KnowledgeEdge]:
        """Get edges by type"""
        return [e for e in self.edges.values() if e.type == edge_type]

    def get_node_degree(self, node_id: str) -> int:
        """Get degree of a node"""
        return len(self.adjacency.get(node_id, [])) + len(self.reverse_adjacency.get(node_id, []))

    def find_path(self, source: str, target: str) -> List[str]:
        """Find path between two nodes (BFS)"""
        if source not in self.nodes or target not in self.nodes:
            return []

        visited = set()
        queue = [[source]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == target:
                return path
            if node not in visited:
                visited.add(node)
                for neighbor in self.adjacency.get(node, []):
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
                for neighbor in self.reverse_adjacency.get(node, []):
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return []

    def get_community(self, node_id: str, max_depth: int = 3) -> List[KnowledgeNode]:
        """Get community around a node"""
        visited = set()
        queue = [(node_id, 0)]
        community = []

        while queue:
            current_id, depth = queue.pop(0)
            if depth > max_depth:
                continue
            if current_id in visited:
                continue
            visited.add(current_id)

            node = self.get_node(current_id)
            if node:
                community.append(node)

            for neighbor in self.adjacency.get(current_id, []):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
            for neighbor in self.reverse_adjacency.get(current_id, []):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))

        return community

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        # Hitung node types
        node_types = {}
        for node in self.nodes.values():
            node_types[node.type] = node_types.get(node.type, 0) + 1
        
        # Hitung edge types
        edge_types = {}
        for edge in self.edges.values():
            edge_types[edge.type] = edge_types.get(edge.type, 0) + 1
        
        # Hitung average degree
        total_degree = sum(self.get_node_degree(n) for n in self.nodes)
        avg_degree = total_degree / len(self.nodes) if self.nodes else 0
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": node_types,
            "edge_types": edge_types,
            "avg_degree": avg_degree,
            "connected_components": self._count_components()
        }

    def _count_components(self) -> int:
        """Count connected components"""
        visited = set()
        components = 0

        for node_id in self.nodes:
            if node_id not in visited:
                components += 1
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        for neighbor in self.adjacency.get(current, []):
                            if neighbor not in visited:
                                stack.append(neighbor)
                        for neighbor in self.reverse_adjacency.get(current, []):
                            if neighbor not in visited:
                                stack.append(neighbor)

        return components

    def export_to_cytoscape(self) -> Dict[str, Any]:
        """Export graph untuk Cytoscape.js visualization"""
        nodes = []
        edges = []

        for node in self.nodes.values():
            nodes.append({
                "data": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type,
                    "confidence": node.confidence
                },
                "classes": node.type
            })

        for edge in self.edges.values():
            edges.append({
                "data": {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.type,
                    "confidence": edge.confidence
                },
                "classes": edge.type
            })

        return {
            "elements": {
                "nodes": nodes,
                "edges": edges
            },
            "stats": self.get_stats()
        }


# Singleton instance
knowledge_graph = KnowledgeGraph()

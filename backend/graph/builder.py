"""Graph Builder - handles graph construction and manipulation"""

from typing import Dict, List, Any, Optional
from backend.graph.models import GraphEntity, GraphRelationship
from backend.graph.metrics import GraphMetrics


class Graph:
    """Graph data structure."""

    def __init__(self):
        self.nodes: Dict[str, Dict] = {}
        self.edges: List[Dict] = []

    def add_node(self, *args, **kwargs):
        """
        Supports:

        Legacy: graph.add_node(GraphNode)
        New:    graph.add_node(node_id, node_type, label, **kwargs)
        """
        # ============================================================
        # LEGACY API: add_node(GraphNode)
        # ============================================================
        if len(args) == 1 and hasattr(args[0], "id"):
            node = args[0]

            node_type = (
                node.type.value
                if hasattr(node.type, "value")
                else str(node.type)
            )

            # ✅ Gunakan kwargs sebagai basis, lalu update dengan canonical
            node_data = dict(node.properties or {})
            node_data.update({
                "id": node.id,
                "type": node_type,
                "label": node.label,
            })

            self.nodes[node.id] = node_data
            return self.nodes[node.id]

        # ============================================================
        # NEW API: add_node(node_id, node_type, label, **kwargs)
        # ============================================================
        if len(args) < 3:
            raise TypeError("add_node() missing required arguments")

        node_id = args[0]
        node_type = args[1]
        label = args[2]

        # ✅ kwargs sebagai basis, lalu update dengan canonical
        node_data = dict(kwargs)
        node_data.update({
            "id": node_id,
            "type": node_type,
            "label": label,
        })

        self.nodes[node_id] = node_data
        return self.nodes[node_id]

    def add_edge(self, *args, **kwargs):
        """
        Supports:

        Legacy: graph.add_edge(GraphEdge)
        New:    graph.add_edge(source, target, edge_type, weight=1.0, **kwargs)
        """
        # ============================================================
        # LEGACY API: add_edge(GraphEdge)
        # ============================================================
        if len(args) == 1 and hasattr(args[0], "source") and hasattr(args[0], "target"):
            edge = args[0]

            edge_type = (
                edge.type.value
                if hasattr(edge.type, "value")
                else str(edge.type)
            )

            # ✅ kwargs sebagai basis, lalu update dengan canonical
            edge_data = dict(edge.properties or {})
            edge_data.update({
                "source": edge.source,
                "target": edge.target,
                "type": edge_type,
                "weight": edge.weight,
            })

            self.edges.append(edge_data)
            return edge_data

        # ============================================================
        # NEW API: add_edge(source, target, edge_type, weight=1.0, **kwargs)
        # ============================================================
        if len(args) < 3:
            raise TypeError("add_edge() missing required arguments")

        source = args[0]
        target = args[1]
        edge_type = args[2]
        weight = args[3] if len(args) > 3 else kwargs.get("weight", 1.0)

        # ✅ kwargs sebagai basis, lalu update dengan canonical
        edge_data = dict(kwargs)
        edge_data.update({
            "source": source,
            "target": target,
            "type": edge_type,
            "weight": weight,
        })

        self.edges.append(edge_data)
        return edge_data

    def get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node."""
        neighbors = []
        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            if source == node_id:
                neighbors.append(target)
            elif target == node_id:
                neighbors.append(source)
        return neighbors

    def get_degree(self, node_id: str) -> int:
        """Get degree of a node (number of neighbors)."""
        return len(self.get_neighbors(node_id))

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID."""
        return self.nodes.get(node_id)

    def get_node_count(self) -> int:
        """Get total number of nodes."""
        return len(self.nodes)

    def get_edge_count(self) -> int:
        """Get total number of edges."""
        return len(self.edges)


from backend.graph.models import GraphNode, GraphEdge

class GraphBuilder:
    """Graph builder for legacy compatibility."""

    def __init__(self):
        self._graph = Graph()

    def add_node(self, node_id: str, node_type, label: str, **kwargs):
        """
        Add node to graph and return GraphNode wrapper.

        Args:
            node_id: Unique node identifier
            node_type: NodeType enum or string
            label: Display label
            **kwargs: Additional properties

        Returns:
            GraphNode: Legacy compatible wrapper with id, type, label, properties.
        """
        # ✅ Normalize node_type to string for internal storage
        node_type_str = (
            node_type.value
            if hasattr(node_type, "value")
            else str(node_type)
        )

        graph_node = self._graph.add_node(
            node_id,
            node_type_str,
            label,
            **kwargs,
        )

        # ✅ Return GraphNode wrapper (with enum type for legacy API)
        return GraphNode(
            id=graph_node["id"],
            type=node_type,
            label=graph_node["label"],
            properties={
                k: v
                for k, v in graph_node.items()
                if k not in ("id", "type", "label")
            }
        )

    def add_edge(self, source: str, target: str, edge_type, weight: float = 1.0, **kwargs):
        """
        Add edge to graph and return GraphEdge wrapper.

        Args:
            source: Source node ID
            target: Target node ID
            edge_type: EdgeType enum or string
            weight: Edge weight (0.0 - 1.0)
            **kwargs: Additional properties

        Returns:
            GraphEdge: Legacy compatible wrapper with source, target, type, weight, properties.
        """
        # ✅ Normalize edge_type to string for internal storage
        edge_type_str = (
            edge_type.value
            if hasattr(edge_type, "value")
            else str(edge_type)
        )

        graph_edge = self._graph.add_edge(
            source,
            target,
            edge_type_str,
            weight,
            **kwargs,
        )

        # ✅ Return GraphEdge wrapper (with enum type for legacy API)
        return GraphEdge(
            source=graph_edge["source"],
            target=graph_edge["target"],
            type=edge_type,
            weight=graph_edge["weight"],
            properties={
                k: v
                for k, v in graph_edge.items()
                if k not in ("source", "target", "type", "weight")
            }
        )

    def get_graph(self) -> Graph:
        """Get internal graph."""
        return self._graph

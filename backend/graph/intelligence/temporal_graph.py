"""
Temporal Graph Engine
Graph dengan dimensi waktu untuk analisis temporal
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TemporalNode:
    """Node dengan temporal information"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    activity_count: int = 0

    def update_activity(self, timestamp: datetime = None) -> None:
        """Update activity timestamp"""
        if timestamp is None:
            timestamp = datetime.now()
        self.last_seen = timestamp
        self.activity_count += 1


@dataclass
class TemporalEdge:
    """Edge dengan temporal information"""
    id: str
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    active_until: Optional[datetime] = None
    confidence: float = 1.0

    def is_active(self, timestamp: datetime = None) -> bool:
        """Check if edge is active at given time"""
        if timestamp is None:
            timestamp = datetime.now()
        if self.active_until:
            return self.created_at <= timestamp <= self.active_until
        return self.created_at <= timestamp


@dataclass
class TemporalSnapshot:
    """Snapshot of graph at a point in time"""
    timestamp: datetime
    nodes: List[TemporalNode]
    edges: List[TemporalEdge]
    metrics: Dict[str, Any] = field(default_factory=dict)


class TemporalGraph:
    """
    Temporal Graph Engine
    Graph dengan dimensi waktu
    """

    def __init__(self):
        self.nodes: Dict[str, TemporalNode] = {}
        self.edges: Dict[str, TemporalEdge] = {}
        self.adjacency: Dict[str, List[Tuple[str, datetime]]] = defaultdict(list)
        self.reverse_adjacency: Dict[str, List[Tuple[str, datetime]]] = defaultdict(list)
        self.snapshots: List[TemporalSnapshot] = []

    def add_node(
        self,
        node_id: str,
        label: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ) -> TemporalNode:
        """Add node to temporal graph"""
        if timestamp is None:
            timestamp = datetime.now()

        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.update_activity(timestamp)
            if properties:
                node.properties.update(properties)
            return node

        node = TemporalNode(
            id=node_id,
            label=label,
            type=node_type,
            properties=properties or {},
            first_seen=timestamp,
            last_seen=timestamp
        )
        self.nodes[node_id] = node
        logger.debug(f"Temporal node added: {label} ({node_id}) at {timestamp}")
        return node

    def add_edge(
        self,
        edge_id: str,
        source: str,
        target: str,
        edge_type: str,
        properties: Optional[Dict[str, Any]] = None,
        confidence: float = 1.0,
        created_at: Optional[datetime] = None,
        active_until: Optional[datetime] = None
    ) -> TemporalEdge:
        """Add edge to temporal graph"""
        if created_at is None:
            created_at = datetime.now()

        if source not in self.nodes:
            raise ValueError(f"Source node {source} not found")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} not found")

        edge = TemporalEdge(
            id=edge_id,
            source=source,
            target=target,
            type=edge_type,
            properties=properties or {},
            created_at=created_at,
            active_until=active_until,
            confidence=confidence
        )
        self.edges[edge_id] = edge
        self.adjacency[source].append((target, created_at))
        self.reverse_adjacency[target].append((source, created_at))

        # Update node activity
        if source in self.nodes:
            self.nodes[source].update_activity(created_at)
        if target in self.nodes:
            self.nodes[target].update_activity(created_at)

        logger.debug(f"Temporal edge added: {source} -> {target} ({edge_type}) at {created_at}")
        return edge

    def get_node_degree(self, node_id: str) -> int:
        """Get degree of a node"""
        return len(self.adjacency.get(node_id, [])) + len(self.reverse_adjacency.get(node_id, []))

    def get_node_at_time(self, node_id: str, timestamp: datetime) -> Optional[TemporalNode]:
        """Get node state at specific time"""
        node = self.nodes.get(node_id)
        if not node:
            return None

        if node.first_seen <= timestamp:
            node_snapshot = TemporalNode(
                id=node.id,
                label=node.label,
                type=node.type,
                properties=node.properties.copy(),
                first_seen=node.first_seen,
                last_seen=node.last_seen if node.last_seen <= timestamp else timestamp,
                activity_count=sum(1 for e in self.edges.values()
                                   if (e.source == node_id or e.target == node_id)
                                   and e.created_at <= timestamp)
            )
            return node_snapshot
        return None

    def get_edges_at_time(self, timestamp: datetime) -> List[TemporalEdge]:
        """Get all edges active at a specific time"""
        return [e for e in self.edges.values() if e.is_active(timestamp)]

    def get_nodes_at_time(self, timestamp: datetime) -> List[TemporalNode]:
        """Get all nodes active at a specific time"""
        result = []
        for node_id in self.nodes:
            node = self.get_node_at_time(node_id, timestamp)
            if node:
                result.append(node)
        return result

    def get_active_nodes(self, timestamp: Optional[datetime] = None) -> List[TemporalNode]:
        """Get currently active nodes"""
        if timestamp is None:
            timestamp = datetime.now()
        return self.get_nodes_at_time(timestamp)

    def get_temporal_neighbors(
        self,
        node_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Tuple[str, datetime]]:
        """Get neighbors within time window"""
        neighbors = set()

        # Outgoing
        for target, time in self.adjacency.get(node_id, []):
            if start_time <= time <= end_time:
                neighbors.add((target, time))

        # Incoming
        for source, time in self.reverse_adjacency.get(node_id, []):
            if start_time <= time <= end_time:
                neighbors.add((source, time))

        return list(neighbors)

    def get_activity_timeline(
        self,
        node_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        interval: str = "day"
    ) -> Dict[str, int]:
        """Get activity timeline for a node"""
        if start_time is None:
            start_time = datetime.now() - timedelta(days=30)
        if end_time is None:
            end_time = datetime.now()

        timeline = defaultdict(int)

        # Count edges involving node
        for edge in self.edges.values():
            if edge.source == node_id or edge.target == node_id:
                if start_time <= edge.created_at <= end_time:
                    key = self._format_time_key(edge.created_at, interval)
                    timeline[key] += 1

        return dict(timeline)

    def _format_time_key(self, timestamp: datetime, interval: str) -> str:
        """Format timestamp based on interval"""
        if interval == "hour":
            return timestamp.strftime("%Y-%m-%d %H:00")
        elif interval == "day":
            return timestamp.strftime("%Y-%m-%d")
        elif interval == "week":
            return timestamp.strftime("%Y-W%W")
        elif interval == "month":
            return timestamp.strftime("%Y-%m")
        return timestamp.strftime("%Y-%m-%d")

    def take_snapshot(self, timestamp: Optional[datetime] = None) -> TemporalSnapshot:
        """Take a snapshot of the graph at a specific time"""
        if timestamp is None:
            timestamp = datetime.now()

        nodes = self.get_nodes_at_time(timestamp)
        edges = self.get_edges_at_time(timestamp)

        snapshot = TemporalSnapshot(
            timestamp=timestamp,
            nodes=nodes,
            edges=edges,
            metrics={
                "node_count": len(nodes),
                "edge_count": len(edges),
                "active_nodes": len([n for n in nodes if n.last_seen >= timestamp - timedelta(hours=24)]),
            }
        )

        self.snapshots.append(snapshot)
        return snapshot

    def get_stats(self) -> Dict[str, Any]:
        """Get temporal graph statistics"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)

        active_now = self.get_active_nodes()
        active_week = self.get_nodes_at_time(week_ago)

        new_nodes = [
            n for n in self.nodes.values()
            if n.first_seen >= week_ago
        ]

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "active_nodes_now": len(active_now),
            "active_nodes_week": len(active_week),
            "new_nodes_week": len(new_nodes),
            "snapshots_taken": len(self.snapshots),
            "node_types": {t: len([n for n in self.nodes.values() if n.type == t])
                          for t in set(n.type for n in self.nodes.values())},
            "edge_types": {t: len([e for e in self.edges.values() if e.type == t])
                          for t in set(e.type for e in self.edges.values())}
        }

    def export_temporal_to_cytoscape(self) -> Dict[str, Any]:
        """Export temporal graph for visualization"""
        nodes = []
        edges = []

        for node in self.nodes.values():
            nodes.append({
                "data": {
                    "id": node.id,
                    "label": node.label,
                    "type": node.type,
                    "first_seen": node.first_seen.isoformat(),
                    "last_seen": node.last_seen.isoformat(),
                    "activity_count": node.activity_count
                }
            })

        for edge in self.edges.values():
            edges.append({
                "data": {
                    "id": edge.id,
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.type,
                    "created_at": edge.created_at.isoformat(),
                    "confidence": edge.confidence
                }
            })

        return {
            "elements": {
                "nodes": nodes,
                "edges": edges
            },
            "temporal_metrics": self.get_stats()
        }


# Singleton instance
_temporal_graph = TemporalGraph()

def get_temporal_graph() -> TemporalGraph:
    """Get singleton instance of TemporalGraph"""
    return _temporal_graph

# Untuk backward compatibility
temporal_graph = _temporal_graph
# backend/lineage/tracker.py

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque


@dataclass
class LineageNode:
    id: str
    node_type: str
    timestamp: datetime
    data: Dict[str, Any]
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Compute deterministic hash for this node."""
        content = json.dumps({
            "id": self.id,
            "type": self.node_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "inputs": self.inputs,
            "outputs": self.outputs
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    # ============================================================
    # LEGACY COMPATIBILITY PROPERTIES
    # ============================================================

    @property
    def type(self) -> str:
        """Legacy compatibility: type alias."""
        return self.node_type

    @property
    def name(self) -> str:
        """Legacy compatibility: name from data."""
        return self.data.get("name", "")


@dataclass
class LineageEdge:
    """Legacy compatibility edge object."""
    source: str
    target: str
    relation: str

    @property
    def type(self) -> str:
        """Legacy compatibility: type alias for relation."""
        return self.relation


class LineageTracker:
    """Track data lineage for audit trails."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # ✅ Initialize _nodes on each instance (singleton reuses it)
        if not hasattr(self, "_nodes"):
            self._nodes: Dict[str, LineageNode] = {}

    def clear(self) -> None:
        """
        Clear in-memory lineage state.

        Intended for unit tests and development only.
        Runtime code should not call this method.
        """
        self._nodes.clear()

    # ============================================================
    # RUNTIME API (Existing)
    # ============================================================

    def add_node(
        self,
        node_type: str,
        data: Dict[str, Any],
        inputs: Optional[List[str]] = None,
        decision_id: Optional[str] = None
    ) -> str:
        """Add a node to the lineage graph (returns node ID)."""
        node_id = decision_id or str(uuid.uuid4())

        node = LineageNode(
            id=node_id,
            node_type=node_type,
            timestamp=datetime.now(),
            data=data,
            inputs=inputs or []
        )
        node.hash = node.compute_hash()

        self._nodes[node_id] = node

        for input_id in node.inputs:
            if input_id in self._nodes:
                if node_id not in self._nodes[input_id].outputs:
                    self._nodes[input_id].outputs.append(node_id)

        return node_id

    def get_lineage(self, node_id: str) -> List[Dict]:
        """Get full lineage chain for a node."""
        lineage = []
        current = self._nodes.get(node_id)

        while current:
            lineage.insert(0, {
                "id": current.id,
                "type": current.node_type,
                "timestamp": current.timestamp.isoformat(),
                "data": current.data,
                "hash": current.hash
            })

            if current.inputs:
                current = self._nodes.get(current.inputs[0])
            else:
                current = None

        return lineage

    def verify_integrity(self, node_id: str) -> bool:
        """Verify hash chain integrity."""
        lineage = self.get_lineage(node_id)

        for i in range(1, len(lineage)):
            prev = lineage[i-1]
            curr = lineage[i]

            node_obj = self._nodes.get(curr["id"])
            if node_obj and node_obj.hash != node_obj.compute_hash():
                return False

            if prev["id"] not in node_obj.inputs if node_obj else True:
                return False

        return True

    def get_decision_path(self, decision_id: str) -> Dict:
        """Get full decision path from input to output."""
        lineage = self.get_lineage(decision_id)

        return {
            "decision_id": decision_id,
            "path_length": len(lineage),
            "inputs": [n for n in lineage if n["type"] == "input"],
            "transforms": [n for n in lineage if n["type"] == "transform"],
            "decision": [n for n in lineage if n["type"] == "decision"],
            "outputs": [n for n in lineage if n["type"] == "output"],
            "verified": self.verify_integrity(decision_id)
        }

    def get_all_nodes(self) -> List[Dict]:
        """Get all lineage nodes."""
        return [
            {
                "id": node.id,
                "type": node.node_type,
                "timestamp": node.timestamp.isoformat(),
                "inputs": node.inputs,
                "outputs": node.outputs,
                "hash": node.hash[:16] + "..."
            }
            for node in self._nodes.values()
        ]

    # ============================================================
    # LEGACY COMPATIBILITY API
    # ============================================================

    def create_node(self, node_type: str, name: str) -> LineageNode:
        """
        Legacy compatibility: create node with name.
        Returns LineageNode object (not ID).
        """
        node_id = self.add_node(
            node_type=node_type,
            data={"name": name}
        )
        return self._nodes[node_id]

    def add_edge(self, source_id: str, target_id: str, relation: str) -> LineageEdge:
        """
        Legacy compatibility: add edge between nodes.
        """
        # Update outputs of source
        if source_id in self._nodes:
            if target_id not in self._nodes[source_id].outputs:
                self._nodes[source_id].outputs.append(target_id)

        # Update inputs of target
        if target_id in self._nodes:
            if source_id not in self._nodes[target_id].inputs:
                self._nodes[target_id].inputs.append(source_id)

        return LineageEdge(source=source_id, target=target_id, relation=relation)

    def get_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """
        Legacy compatibility: BFS to find path between nodes.
        """
        if start_id not in self._nodes or end_id not in self._nodes:
            return None

        queue = deque([(start_id, [start_id])])
        visited = {start_id}

        while queue:
            current, path = queue.popleft()
            if current == end_id:
                return path

            node = self._nodes.get(current)
            if node:
                for neighbor in node.outputs:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        return None

    def get_metrics(self) -> Dict[str, Any]:
        """
        Legacy compatibility: get node metrics.
        """
        node_count = len(self._nodes)
        node_types: Dict[str, int] = {}

        for node in self._nodes.values():
            node_type = node.node_type
            node_types[node_type] = node_types.get(node_type, 0) + 1

        return {
            "node_count": node_count,
            "node_types": node_types,
        }


# Singleton instance
tracker = LineageTracker()
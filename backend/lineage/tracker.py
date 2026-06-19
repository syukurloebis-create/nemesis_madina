"""Lineage Tracking - Trace decision from input to output"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class LineageNode:
    id: str
    node_type: str  # input, transform, decision, output
    timestamp: datetime
    data: Dict[str, Any]
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """Compute deterministic hash for this node"""
        content = json.dumps({
            "id": self.id,
            "type": self.node_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "inputs": self.inputs,
            "outputs": self.outputs
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

class LineageTracker:
    """Track data lineage for audit trails"""
    
    _instance = None
    _nodes: Dict[str, LineageNode] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def add_node(
        self,
        node_type: str,
        data: Dict[str, Any],
        inputs: Optional[List[str]] = None,
        decision_id: Optional[str] = None
    ) -> str:
        """Add a node to the lineage graph"""
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
        
        # Update outputs of input nodes
        for input_id in node.inputs:
            if input_id in self._nodes:
                if node_id not in self._nodes[input_id].outputs:
                    self._nodes[input_id].outputs.append(node_id)
        
        return node_id
    
    def get_lineage(self, node_id: str) -> List[Dict]:
        """Get full lineage chain for a node"""
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
        """Verify hash chain integrity"""
        lineage = self.get_lineage(node_id)
        
        for i in range(1, len(lineage)):
            prev = lineage[i-1]
            curr = lineage[i]
            
            # Verify current node's hash
            node_obj = self._nodes.get(curr["id"])
            if node_obj and node_obj.hash != node_obj.compute_hash():
                return False
            
            # Verify linkage
            if prev["id"] not in node_obj.inputs if node_obj else True:
                return False
        
        return True
    
    def get_decision_path(self, decision_id: str) -> Dict:
        """Get full decision path from input to output"""
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
        """Get all lineage nodes"""
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

# Singleton instance
tracker = LineageTracker()

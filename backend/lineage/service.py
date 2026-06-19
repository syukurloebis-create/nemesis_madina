from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class LineageTracker:
    _nodes: Dict[str, Dict] = {}
    
    def add_node(self, node_type: str, data: Dict, inputs: List[str] = None) -> str:
        node_id = str(uuid.uuid4())
        self._nodes[node_id] = {
            "id": node_id,
            "type": node_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "inputs": inputs or [],
            "outputs": []
        }
        for inp in inputs or []:
            if inp in self._nodes:
                self._nodes[inp]["outputs"].append(node_id)
        return node_id
    
    def get_lineage(self, node_id: str) -> List[Dict]:
        lineage = []
        current = self._nodes.get(node_id)
        while current:
            lineage.insert(0, current)
            if current.get("inputs") and current["inputs"]:
                current = self._nodes.get(current["inputs"][0])
            else:
                current = None
        return lineage

tracker = LineageTracker()

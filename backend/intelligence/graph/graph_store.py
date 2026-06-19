"""
Graph Store - In-memory storage (synchronous for now)
"""

import hashlib
import json
import logging
from typing import Dict, List, Any, Set
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class GraphStore:
    """Simple in-memory graph storage"""
    
    def __init__(self):
        self._graphs = {}
    
    def get_graph(self, case_id: str) -> Dict:
        if case_id not in self._graphs:
            self._graphs[case_id] = {
                "nodes": [],
                "nodes_set": set(),
                "edges": [],
                "edges_set": set(),
                "version": None,
            }
        return self._graphs[case_id]
    
    def add_node(self, case_id: str, node_id: str, node_type: str, name: str, **attrs) -> bool:
        graph = self.get_graph(case_id)
        if node_id not in graph["nodes_set"]:
            graph["nodes_set"].add(node_id)
            graph["nodes"].append({
                "id": node_id,
                "type": node_type,
                "name": name,
                "attributes": attrs,
            })
            return True
        return False
    
    def add_edge(self, case_id: str, source: str, target: str, edge_type: str, **props) -> bool:
        graph = self.get_graph(case_id)
        edge_key = f"{source}→{target}"
        if edge_key not in graph["edges_set"]:
            graph["edges_set"].add(edge_key)
            graph["edges"].append({
                "source": source,
                "target": target,
                "type": edge_type,
                "properties": props,
            })
            return True
        return False
    
    def add_entities(self, case_id: str, entities: List[Dict]) -> int:
        added = 0
        for e in entities:
            node_id = f"{e.get('type', 'unknown')}:{e.get('name', '')}"
            if self.add_node(case_id, node_id, e.get('type', 'unknown'), e.get('name', '')):
                added += 1
        return added
    
    def add_transactions(self, case_id: str, transactions: List[Dict]) -> int:
        added = 0
        for tx in transactions:
            from_name = tx.get('from', '')
            to_name = tx.get('to', '')
            if from_name and to_name:
                from_node = f"company:{from_name}"
                to_node = f"company:{to_name}"
                if self.add_edge(case_id, from_node, to_node, "financial_transfer"):
                    added += 1
        return added
    
    def get_nodes(self, case_id: str) -> List[Dict]:
        return self.get_graph(case_id)["nodes"]
    
    def get_edges(self, case_id: str) -> List[Dict]:
        return self.get_graph(case_id)["edges"]
    
    def get_graph_summary(self, case_id: str) -> Dict:
        graph = self.get_graph(case_id)
        return {
            "case_id": case_id,
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "has_data": len(graph["nodes"]) > 0,
        }
    
    def case_exists(self, case_id: str) -> bool:
        return case_id in self._graphs
    
    def clear_case(self, case_id: str):
        if case_id in self._graphs:
            del self._graphs[case_id]
            return True
        return False


graph_store = GraphStore()
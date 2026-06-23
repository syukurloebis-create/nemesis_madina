"""
Lineage Graph - Visualization and Query Support
"""

from typing import List, Dict, Any, Set, Optional
from lineage.tracker import LineageTracker, LineageNode, LineageEdge


class LineageGraph:
    """Lineage graph with query capabilities"""
    
    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
    
    def get_subgraph(self, node_ids: Set[str]) -> Dict[str, Any]:
        """Extract subgraph containing specified nodes"""
        subgraph = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node_id in node_ids:
            if node_id in self.tracker.nodes:
                node = self.tracker.nodes[node_id]
                subgraph["nodes"].append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "timestamp": node.timestamp.isoformat()
                })
        
        # Add edges between these nodes
        for edge in self.tracker.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph["edges"].append({
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship
                })
        
        return subgraph
    
    def get_upstream_dependencies(self, node_id: str, depth: int = 3) -> List[Dict]:
        """Get upstream dependencies (inputs)"""
        dependencies = []
        
        def collect(current_id: str, current_depth: int):
            if current_depth > depth:
                return
            
            node = self.tracker.nodes.get(current_id)
            if node:
                dependencies.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "depth": current_depth
                })
                
                for input_id in node.inputs:
                    collect(input_id, current_depth + 1)
        
        collect(node_id, 0)
        return dependencies
    
    def get_downstream_dependents(self, node_id: str, depth: int = 3) -> List[Dict]:
        """Get downstream dependents (outputs)"""
        dependents = []
        
        def collect(current_id: str, current_depth: int):
            if current_depth > depth:
                return
            
            node = self.tracker.nodes.get(current_id)
            if node:
                dependents.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "depth": current_depth
                })
                
                for output_id in node.outputs:
                    collect(output_id, current_depth + 1)
        
        collect(node_id, 0)
        return dependents
    
    def get_critical_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Get critical path (longest path) between nodes"""
        # Simplified: use get_path from tracker
        return self.tracker.get_path(start_id, end_id)
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """Export graph for visualization (D3.js, Cytoscape.js)"""
        return {
            "nodes": [
                {
                    "data": {
                        "id": n.id,
                        "label": n.name,
                        "type": n.type
                    }
                }
                for n in self.tracker.nodes.values()
            ],
            "edges": [
                {
                    "data": {
                        "id": f"{e.source}_{e.target}",
                        "source": e.source,
                        "target": e.target,
                        "label": e.relationship
                    }
                }
                for e in self.tracker.edges
            ]
        }

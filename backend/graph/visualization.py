"""
Advanced Graph Visualization for Collusion Networks
D3.js / Cytoscape.js compatible JSON output
"""

from typing import List, Dict, Any
from collections import defaultdict


class GraphVisualization:
    """
    Generate visualization-ready graph data for D3.js / Cytoscape.js
    """
    
    def to_cytoscape_json(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """Convert to Cytoscape.js format"""
        elements = []
        
        # Add nodes
        for node in nodes:
            elements.append({
                "data": {
                    "id": node.get("id"),
                    "label": node.get("name"),
                    "type": node.get("type"),
                },
                "classes": f"node-type-{node.get('type', 'unknown')}",
                "position": self._calculate_position(len(elements))
            })
        
        # Add edges
        for edge in edges:
            elements.append({
                "data": {
                    "id": f"{edge.get('source')}_{edge.get('target')}",
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "label": edge.get("type", "transfer"),
                    "amount": edge.get("properties", {}).get("amount", 0),
                },
                "classes": f"edge-type-{edge.get('type', 'transfer')}"
            })
        
        return {
            "elements": elements,
            "style": self._get_cytoscape_style(),
            "layout": {
                "name": "cose",
                "idealEdgeLength": 100,
                "nodeOverlap": 20,
                "refresh": 20,
                "fit": True,
                "padding": 30,
                "randomize": False,
                "componentSpacing": 100,
                "nodeRepulsion": 400000,
                "edgeElasticity": 100,
                "gravity": 80,
                "numIter": 1000,
                "initialTemp": 200,
                "coolingFactor": 0.95,
                "minTemp": 1.0,
            }
        }
    
    def to_d3_json(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """Convert to D3.js force-directed graph format"""
        return {
            "nodes": [
                {
                    "id": n.get("id"),
                    "name": n.get("name"),
                    "type": n.get("type"),
                    "group": self._get_node_group(n.get("type")),
                }
                for n in nodes
            ],
            "links": [
                {
                    "source": e.get("source"),
                    "target": e.get("target"),
                    "value": e.get("properties", {}).get("amount", 1),
                    "type": e.get("type"),
                }
                for e in edges
            ],
        }
    
    def highlight_collusion_cycle(self, nodes: List[Dict], edges: List[Dict], cycle: List[str]) -> Dict:
        """Highlight collusion cycle in the graph"""
        data = self.to_cytoscape_json(nodes, edges)
        
        # Add classes for highlighting
        for element in data["elements"]:
            if "data" in element:
                node_id = element["data"].get("id")
                if node_id in cycle:
                    element["classes"] = element.get("classes", "") + " highlight-cycle"
        
        return data
    
    def _calculate_position(self, index: int) -> Dict:
        """Calculate initial position for node"""
        import math
        radius = 200
        angle = (index * 137.5) * math.pi / 180  # Golden angle
        
        return {
            "x": radius * math.cos(angle),
            "y": radius * math.sin(angle),
        }
    
    def _get_node_group(self, node_type: str) -> int:
        """Get group number for node type"""
        groups = {
            "company": 1,
            "person": 2,
            "account": 3,
            "asset": 4,
        }
        return groups.get(node_type, 5)
    
    def _get_cytoscape_style(self) -> List[Dict]:
        """Get Cytoscape.js style configuration"""
        return [
            {
                "selector": "node",
                "style": {
                    "width": "mapData(score, 0, 1, 30, 80)",
                    "height": "mapData(score, 0, 1, 30, 80)",
                    "content": "data(label)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "background-color": "#1f77b4",
                    "border-width": 2,
                    "border-color": "#fff",
                }
            },
            {
                "selector": "node.highlight-cycle",
                "style": {
                    "background-color": "#ff6b6b",
                    "border-width": 3,
                    "border-color": "#ff0000",
                }
            },
            {
                "selector": "edge",
                "style": {
                    "width": 2,
                    "line-color": "#ccc",
                    "target-arrow-color": "#ccc",
                    "target-arrow-shape": "triangle",
                    "curve-style": "bezier",
                    "label": "data(label)",
                }
            },
            {
                "selector": "edge.highlight-cycle",
                "style": {
                    "line-color": "#ff6b6b",
                    "target-arrow-color": "#ff6b6b",
                    "width": 4,
                }
            },
            {
                "selector": ".node-type-person",
                "style": {
                    "background-color": "#2ecc71",
                    "shape": "ellipse",
                }
            },
            {
                "selector": ".node-type-company",
                "style": {
                    "background-color": "#3498db",
                    "shape": "rectangle",
                }
            },
            {
                "selector": ".node-type-account",
                "style": {
                    "background-color": "#e74c3c",
                    "shape": "diamond",
                }
            },
        ]


visualizer = GraphVisualization()
"""
Graph Intelligence V8+
Analisis relasi antar entity (vendor, kontrak, event)
"""

from typing import Dict, List


class GraphIntelligence:

    def build_graph(self, events: List[Dict]) -> Dict:

        nodes = set()
        edges = []

        for e in events:
            entity = e.get("entity_id", "unknown")
            vendor = e.get("payload", {}).get("vendor", "unknown")

            nodes.add(entity)
            nodes.add(vendor)

            edges.append({
                "from": entity,
                "to": vendor,
                "type": "PROCUREMENT"
            })

        return {
            "nodes": list(nodes),
            "edges": edges,
            "density": len(edges) / max(len(nodes), 1)
        }
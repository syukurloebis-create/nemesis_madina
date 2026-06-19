# graph/engine/graph_builder.py - Graph Intelligence
class GraphIntelligenceEngine:
    @staticmethod
    def build_investigation_graph(entities, relationships):
        edge_weights = {
            "VENDOR_WON_PACKAGE": 0.8,
            "PACKAGE_HAS_VALUE": 0.6,
            "VENDOR_SHARED_OWNER": 0.9,
            "VENDOR_REPEAT_WINNER": 0.8
        }
        meaningful_edges = []
        for rel in relationships:
            weight = edge_weights.get(rel.get("type"), 0.3)
            if weight >= 0.5:
                meaningful_edges.append({**rel, "weight": weight})
        return {"total_entities": len(entities), "meaningful_edges": len(meaningful_edges)}

# backend/graph/relationship_builder.py
class RelationshipBuilder:
    async def build_entity_graph(
        self,
        entity_type: str,
        depth: int = 3
    ) -> Dict:
        """Bangun graph hubungan entitas"""
        edges = await self.db.fetch("""
            SELECT source_entity, target_entity, relationship_type
            FROM entity_edges
            WHERE source_entity LIKE $1 OR target_entity LIKE $1
        """, f'%{entity_type}%')
        
        return {
            "nodes": self._extract_nodes(edges),
            "edges": edges,
            "metrics": self._compute_metrics(edges)
        }
    
    async def detect_collusion(self, threshold: float = 0.7) -> List[Dict]:
        """Deteksi potensi kolusi"""
        # Implementasi collusion detection
        pass


def should_create_edge(score: float, meta: dict) -> bool:
    # 1. similarity threshold hard gate
    if score < 0.75:
        return False

    # 2. prevent over-density per node
    if meta.get("source_degree", 0) > 120:
        return False

    # 3. prevent duplicate semantic edges
    if meta.get("same_entity_alias", False):
        return False

    return True


def should_keep_edge(edge):
    if edge.weight < 0.5:
        return False

    if edge.shared_packages <= 1:
        return False

    return True
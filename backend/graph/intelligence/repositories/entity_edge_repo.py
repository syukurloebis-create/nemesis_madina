"""Entity Edge Repository - Graph database operations"""

import asyncpg
from typing import Optional, List, Dict, Any, Set
from uuid import UUID
import json
from datetime import datetime

from graph.intelligence.models import (
    EntityNode, EntityEdge, RelationshipType, EntityType, NetworkMetrics
)


class EntityEdgeRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def add_node(self, node: EntityNode) -> EntityNode:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO entity_nodes (node_id, entity_type, name, properties, first_seen, last_seen, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (node_id) DO UPDATE SET
                    last_seen = EXCLUDED.last_seen,
                    properties = EXCLUDED.properties
            """,
                node.node_id,
                node.entity_type.value if hasattr(node.entity_type, 'value') else node.entity_type,
                node.name,
                json.dumps(node.properties),
                node.first_seen,
                node.last_seen,
                json.dumps(node.metadata)
            )
            return node
    
    async def add_edge(self, edge: EntityEdge) -> EntityEdge:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO entity_edges (
                    edge_id, source_id, target_id, relationship_type,
                    weight, confidence, evidence_ids, first_seen, last_seen, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (source_id, target_id, relationship_type) DO UPDATE SET
                    weight = EXCLUDED.weight,
                    confidence = EXCLUDED.confidence,
                    last_seen = EXCLUDED.last_seen
            """,
                edge.edge_id,
                edge.source_id,
                edge.target_id,
                edge.relationship_type.value if hasattr(edge.relationship_type, 'value') else edge.relationship_type,
                edge.weight,
                edge.confidence,
                [str(eid) for eid in edge.evidence_ids],
                edge.first_seen,
                edge.last_seen,
                json.dumps(edge.metadata)
            )
            return edge
    
    async def get_neighbors(
        self,
        node_id: str,
        depth: int = 1,
        relationship_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                WITH RECURSIVE neighbors AS (
                    SELECT source_id, target_id, relationship_type, 1 as depth
                    FROM entity_edges 
                    WHERE source_id = $1 OR target_id = $1
                    
                    UNION ALL
                    
                    SELECT e.source_id, e.target_id, e.relationship_type, n.depth + 1
                    FROM entity_edges e
                    INNER JOIN neighbors n ON e.source_id = n.target_id OR e.target_id = n.source_id
                    WHERE n.depth < $2
                )
                SELECT DISTINCT source_id as node_id, relationship_type, depth
                FROM neighbors
                WHERE source_id != $1
                LIMIT $3
            """, node_id, depth, 100)
            
            return [dict(row) for row in rows]
    
    async def get_relationships(
        self,
        source_id: str,
        target_id: str
    ) -> List[EntityEdge]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM entity_edges 
                WHERE (source_id = $1 AND target_id = $2) 
                   OR (source_id = $2 AND target_id = $1)
            """, source_id, target_id)
            return [self._row_to_edge(row) for row in rows]
    
    async def get_network_metrics(self):
        async with self.pool.acquire() as conn:
            node_count = await conn.fetchval("SELECT COUNT(DISTINCT node_id) FROM entity_nodes")
            edge_count = await conn.fetchval("SELECT COUNT(*) FROM entity_edges")
            
            central = await conn.fetch("""
                SELECT node_id, COUNT(*) as degree
                FROM (
                    SELECT source_id as node_id FROM entity_edges
                    UNION ALL
                    SELECT target_id as node_id FROM entity_edges
                ) as all_nodes
                GROUP BY node_id
                ORDER BY degree DESC
                LIMIT 10
            """)
            
            return {
                "node_count": node_count,
                "edge_count": edge_count,
                "density": edge_count / (node_count * (node_count - 1)) if node_count > 1 else 0,
                "clustering_coefficient": 0,
                "connected_components": 0,
                "central_nodes": [{"node_id": row['node_id'], "degree": row['degree']} for row in central]
            }
    
    async def find_connected_entities(
        self,
        entity_id: str,
        max_depth: int = 3
    ) -> List[str]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                WITH RECURSIVE connected AS (
                    SELECT source_id, target_id, 1 as depth
                    FROM entity_edges 
                    WHERE source_id = $1 OR target_id = $1
                    
                    UNION ALL
                    
                    SELECT e.source_id, e.target_id, c.depth + 1
                    FROM entity_edges e
                    INNER JOIN connected c ON e.source_id = c.target_id OR e.target_id = c.source_id
                    WHERE c.depth < $2
                )
                SELECT DISTINCT source_id as entity_id FROM connected
                WHERE source_id != $1
                UNION
                SELECT DISTINCT target_id as entity_id FROM connected
                WHERE target_id != $1
                LIMIT 1000
            """, entity_id, max_depth)
            
            return [row['entity_id'] for row in rows]
    
    def _row_to_edge(self, row) -> EntityEdge:
        from graph.intelligence.models import EntityEdge, RelationshipType
        return EntityEdge(
            edge_id=row['edge_id'],
            source_id=row['source_id'],
            target_id=row['target_id'],
            relationship_type=row['relationship_type'],
            weight=row['weight'],
            confidence=row['confidence'],
            evidence_ids=[UUID(eid) for eid in row['evidence_ids']] if row['evidence_ids'] else [],
            first_seen=row['first_seen'],
            last_seen=row['last_seen'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )

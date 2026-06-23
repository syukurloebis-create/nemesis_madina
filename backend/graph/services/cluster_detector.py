# graph/services/cluster_detector.py - Fraud Cluster Detection
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ClusterDetector:
    """Detect suspicious clusters in graph"""
    
    def __init__(self, session: AsyncSession, case_id: str):
        self.session = session
        self.case_id = case_id
    
    async def detect_suspicious_clusters(self) -> List[Dict[str, Any]]:
        """Detect clusters with fraud signals"""
        logger.info("🔍 Detecting suspicious clusters...")
        
        # 1. Find connected components with shared packages
        result = await self.session.execute(text("""
            WITH RECURSIVE cluster AS (
                SELECT 
                    source_id as node_id,
                    source_id as cluster_id,
                    0 as depth
                FROM graph_relationships
                WHERE relationship_type = 'shared_package'
                  AND case_id = :case_id
                
                UNION
                
                SELECT 
                    r.target_id,
                    c.cluster_id,
                    c.depth + 1
                FROM cluster c
                JOIN graph_relationships r ON r.source_id = c.node_id
                WHERE r.relationship_type = 'shared_package'
                  AND r.case_id = :case_id
                  AND c.depth < 5
            )
            SELECT 
                cluster_id,
                COUNT(DISTINCT node_id) as member_count,
                STRING_AGG(DISTINCT e.name, ', ') as members
            FROM cluster c
            JOIN graph_entities e ON e.id = c.node_id
            GROUP BY cluster_id
            HAVING COUNT(DISTINCT node_id) >= 3
            ORDER BY member_count DESC
            LIMIT 20
        """), {"case_id": self.case_id})
        
        clusters = result.fetchall()
        
        # 2. Enrich each cluster with risk signals
        enriched = []
        for row in clusters:
            enriched.append({
                "cluster_id": str(row[0]),
                "member_count": row[1],
                "members": row[2].split(', ') if row[2] else [],
                "risk_signals": await self._get_cluster_signals(row[0])
            })
        
        logger.info(f"  ✅ Found {len(enriched)} suspicious clusters")
        return enriched
    
    async def _get_cluster_signals(self, cluster_id: str) -> Dict[str, Any]:
        """Get risk signals for a cluster"""
        result = await self.session.execute(text("""
            SELECT 
                COUNT(DISTINCT relationship_type) as type_count,
                AVG(weight) as avg_weight,
                COUNT(*) as edge_count
            FROM graph_relationships r
            JOIN graph_entities e1 ON e1.id = r.source_id
            JOIN graph_entities e2 ON e2.id = r.target_id
            WHERE r.case_id = :case_id
              AND (e1.id = :cluster_id OR e2.id = :cluster_id)
        """), {"case_id": self.case_id, "cluster_id": cluster_id})
        row = result.fetchone()
        
        return {
            "type_count": row[0] or 0,
            "avg_weight": float(row[1] or 0),
            "edge_count": row[2] or 0,
            "risk_level": "HIGH" if row[1] and row[1] > 70 else "MEDIUM"
        }

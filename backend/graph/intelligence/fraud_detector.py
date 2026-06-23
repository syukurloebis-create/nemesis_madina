# graph/intelligence/fraud_detector.py - Fraud Pattern Detection (FIXED)
import logging
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class FraudDetector:
    """Detect fraud patterns in graph"""
    
    def __init__(self, session: AsyncSession, case_id: str):
        self.session = session
        self.case_id = case_id
    
    async def detect_fraud_signals(self) -> Dict[str, Any]:
        logger.info("🔍 Detecting fraud signals...")
        signals = {
            "high_risk_clusters": await self._detect_high_risk_clusters(),
            "hub_entities": await self._detect_hub_entities(),
            "shared_package_patterns": await self._detect_shared_package_patterns(),
            "method_similarity_patterns": await self._detect_method_similarity()
        }
        signals["overall_risk"] = await self._calculate_overall_risk(signals)
        return signals
    
    async def _detect_high_risk_clusters(self) -> List[Dict[str, Any]]:
        # ============ FIX: Hapus gc.case_id ============
        result = await self.session.execute(text("""
            SELECT
                gc.cluster_id,
                COUNT(gc.entity_id) as member_count,
                AVG(gns.pagerank) as avg_pagerank,
                AVG(r.weight) as avg_weight
            FROM graph_clusters gc
            JOIN graph_node_scores gns ON gns.entity_id::VARCHAR = gc.entity_id::VARCHAR
            JOIN graph_relationships r ON r.source_id::VARCHAR = gc.entity_id::VARCHAR
            WHERE r.case_id::VARCHAR = :case_id
            GROUP BY gc.cluster_id
            HAVING COUNT(gc.entity_id) >= 3
              AND AVG(r.weight) > 60
            ORDER BY member_count DESC
            LIMIT 10
        """), {"case_id": self.case_id})
        
        clusters = result.fetchall()
        return [
            {
                "cluster_id": row[0],
                "member_count": row[1],
                "avg_pagerank": float(row[2] or 0),
                "avg_weight": float(row[3] or 0),
                "risk_level": "HIGH" if row[2] and row[2] > 0.02 else "MEDIUM"
            }
            for row in clusters
        ]
    
    async def _detect_hub_entities(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(text("""
            SELECT 
                e.name,
                COUNT(r.id) as degree,
                AVG(r.weight) as avg_weight,
                gns.pagerank
            FROM graph_entities e
            JOIN graph_relationships r ON r.source_id::VARCHAR = e.id::VARCHAR
            JOIN graph_node_scores gns ON gns.entity_id::VARCHAR = e.id::VARCHAR
            WHERE e.case_id::VARCHAR = :case_id
            GROUP BY e.name, gns.pagerank
            HAVING COUNT(r.id) > 100
            ORDER BY degree DESC
            LIMIT 20
        """), {"case_id": self.case_id})
        
        rows = result.fetchall()
        return [
            {
                "name": row[0],
                "degree": row[1],
                "avg_weight": float(row[2] or 0),
                "pagerank": float(row[3] or 0),
                "risk_level": "HIGH" if row[1] > 500 else "MEDIUM"
            }
            for row in rows
        ]
    
    async def _detect_shared_package_patterns(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(text("""
            SELECT 
                r.source_id,
                r.target_id,
                r.weight,
                e1.name as source_name,
                e2.name as target_name
            FROM graph_relationships r
            JOIN graph_entities e1 ON e1.id::VARCHAR = r.source_id::VARCHAR
            JOIN graph_entities e2 ON e2.id::VARCHAR = r.target_id::VARCHAR
            WHERE r.relationship_type = 'shared_package'
              AND r.weight >= 90
              AND r.case_id::VARCHAR = :case_id
            ORDER BY r.weight DESC
            LIMIT 20
        """), {"case_id": self.case_id})
        
        rows = result.fetchall()
        return [
            {
                "source": row[3],
                "target": row[4],
                "weight": float(row[2] or 0),
                "pattern": "high_confidence_shared_package"
            }
            for row in rows
        ]
    
    async def _detect_method_similarity(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(text("""
            SELECT 
                r.source_id,
                r.target_id,
                r.weight,
                e1.name as source_name,
                e2.name as target_name
            FROM graph_relationships r
            JOIN graph_entities e1 ON e1.id::VARCHAR = r.source_id::VARCHAR
            JOIN graph_entities e2 ON e2.id::VARCHAR = r.target_id::VARCHAR
            WHERE r.relationship_type = 'method_similarity'
              AND r.weight >= 65
              AND r.case_id::VARCHAR = :case_id
            ORDER BY r.weight DESC
            LIMIT 20
        """), {"case_id": self.case_id})
        
        rows = result.fetchall()
        return [
            {
                "source": row[3],
                "target": row[4],
                "weight": float(row[2] or 0),
                "pattern": "high_confidence_method_similarity"
            }
            for row in rows
        ]
    
    async def _calculate_overall_risk(self, signals: Dict[str, Any]) -> str:
        risk_score = 0
        risk_score += len(signals.get("high_risk_clusters", [])) * 10
        risk_score += len([h for h in signals.get("hub_entities", []) if h.get("risk_level") == "HIGH"]) * 5
        risk_score += len(signals.get("shared_package_patterns", [])) * 2
        
        if risk_score >= 50:
            return "CRITICAL"
        elif risk_score >= 30:
            return "HIGH"
        elif risk_score >= 15:
            return "MEDIUM"
        else:
            return "LOW"

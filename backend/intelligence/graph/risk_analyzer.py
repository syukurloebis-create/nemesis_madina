# intelligence/graph/risk_analyzer.py - Graph Risk Analyzer (ENHANCED)
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class GraphRiskAnalyzer:
    """Analyze graph for risk signals - ENHANCED VERSION"""
    
    @staticmethod
    async def calculate_graph_risk(case_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Calculate graph-based risk score with enhanced metrics"""
        try:
            # 1. Basic metrics
            query = """
                SELECT
                    COUNT(DISTINCT e.id) as total_entities,
                    COUNT(DISTINCT r.id) as total_edges,
                    AVG(r.weight) as avg_weight,
                    COUNT(DISTINCT r.relationship_type) as type_count
                FROM graph_entities e
                LEFT JOIN graph_relationships r ON 
                    r.source_id = e.id OR r.target_id = e.id
                WHERE e.case_id = :case_id
            """
            result = await db.execute(text(query), {"case_id": case_id})
            row = result.fetchone()
            
            entities = row[0] or 0
            edges = row[1] or 0
            avg_weight = float(row[2] or 0)
            type_count = row[3] or 0
            
            if entities == 0:
                return {
                    "graph_risk": 0,
                    "level": "NO_DATA",
                    "entities": 0,
                    "edges": 0,
                    "confidence": 0,
                    "data_source": "none"
                }
            
            # ============ ENHANCED RISK CALCULATION ============
            # 1. Density score (0-30)
            max_possible = entities * (entities - 1) / 2
            density = edges / max_possible if max_possible > 0 else 0
            density_score = min(density * 100, 30)
            
            # 2. Weight score (0-30)
            weight_score = (avg_weight / 100) * 30 if avg_weight > 0 else 0
            
            # 3. Diversity score (0-20)
            diversity_score = (type_count / 4) * 20
            
            # 4. Edge count score (0-20)
            # Normalize: 0 edges = 0, 500+ edges = 20
            edge_score = min((edges / 500) * 20, 20)
            
            # Final score
            graph_risk = int(density_score + weight_score + diversity_score + edge_score)
            graph_risk = min(max(graph_risk, 0), 100)
            
            # Level
            if graph_risk >= 60:
                level = "HIGH"
            elif graph_risk >= 30:
                level = "MEDIUM"
            else:
                level = "LOW"
            
            return {
                "graph_risk": graph_risk,
                "level": level,
                "entities": entities,
                "edges": edges,
                "avg_weight": round(avg_weight, 2),
                "type_count": type_count,
                "confidence": 85 if entities > 0 else 0,
                "data_source": "exact_match",
                "metrics": {
                    "density_score": round(density_score, 2),
                    "weight_score": round(weight_score, 2),
                    "diversity_score": round(diversity_score, 2),
                    "edge_score": round(edge_score, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating graph risk: {str(e)}")
            return {
                "graph_risk": 0,
                "level": "UNKNOWN",
                "entities": 0,
                "edges": 0,
                "error": str(e)
            }

    @staticmethod
    async def get_cluster_risk(case_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get cluster-based risk signal"""
        try:
            from graph.services.cluster_detector import ClusterDetector
            detector = ClusterDetector(db, case_id)
            clusters = await detector.detect_suspicious_clusters()
            
            high_risk_clusters = [c for c in clusters if c.get("risk_signals", {}).get("risk_level") == "HIGH"]
            
            return {
                "total_clusters": len(clusters),
                "high_risk_clusters": len(high_risk_clusters),
                "clusters": clusters[:5],
                "risk_contribution": min(len(high_risk_clusters) * 10, 30)
            }
        except Exception as e:
            logger.error(f"Error getting cluster risk: {str(e)}")
            return {"total_clusters": 0, "high_risk_clusters": 0, "clusters": [], "risk_contribution": 0}

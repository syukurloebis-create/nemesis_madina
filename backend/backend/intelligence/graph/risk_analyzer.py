# graph/risk_analyzer.py - Graph Risk Analyzer (FIXED)
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class GraphRiskAnalyzer:
    """Analyze graph for risk signals using graph_relationships table"""

    @staticmethod
    async def calculate_graph_risk(case_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Calculate graph-based risk score"""
        try:
            # Debug: cek apakah ada data dengan case_id
            check_query = "SELECT COUNT(*) FROM graph_entities WHERE case_id = :case_id"
            check_result = await db.execute(text(check_query), {"case_id": case_id})
            count = check_result.scalar() or 0
            
            if count == 0:
                logger.warning(f"No graph data found for case_id: {case_id}")
                return {
                    "graph_risk": 0,
                    "level": "NO_DATA",
                    "entities": 0,
                    "edges": 0,
                    "warning": f"Tidak ada data graph untuk case {case_id}"
                }
            
            # Main query
            query = """
                SELECT 
                    COUNT(DISTINCT e.id) as total_entities,
                    COUNT(DISTINCT r.id) as total_edges
                FROM graph_entities e
                LEFT JOIN graph_relationships r ON 
                    r.source_id = e.id OR r.target_id = e.id
                WHERE e.case_id = :case_id
            """
            result = await db.execute(text(query), {"case_id": case_id})
            row = result.fetchone()
            
            entities = row[0] or 0
            edges = row[1] or 0
            
            if entities <= 1:
                graph_risk = 0
                level = "LOW"
            else:
                density = (2 * edges) / (entities * (entities - 1))
                graph_risk = min(density * 100, 100)
                level = "HIGH" if graph_risk >= 60 else "MEDIUM" if graph_risk >= 40 else "LOW"
            
            return {
                "graph_risk": round(graph_risk, 2),
                "level": level,
                "entities": entities,
                "edges": edges,
                "case_id": case_id
            }
        except Exception as e:
            logger.error(f"Error calculating graph risk: {str(e)}")
            return {"graph_risk": 0, "level": "UNKNOWN", "error": str(e)}

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
            # ============ FIX: Cek data dengan case_id ============
            # Cek exact match dulu
            exact_query = """
                SELECT COUNT(*) 
                FROM graph_entities 
                WHERE case_id = :case_id AND case_id != ''
            """
            exact_result = await db.execute(text(exact_query), {"case_id": case_id})
            exact_match = exact_result.scalar() or 0
            
            # Jika tidak ada exact match, cek NULL data
            if exact_match == 0:
                logger.info(f"No exact match for case {case_id}, checking fallback...")
                fallback_query = """
                    SELECT COUNT(*) 
                    FROM graph_entities 
                    WHERE case_id IS NULL OR case_id = ''
                """
                fallback_result = await db.execute(text(fallback_query))
                fallback_count = fallback_result.scalar() or 0
                
                if fallback_count == 0:
                    return {
                        "graph_risk": 0,
                        "level": "NO_DATA",
                        "entities": 0,
                        "edges": 0,
                        "warning": f"Tidak ada data graph untuk case {case_id}",
                        "data_source": "none"
                    }
                
                # Gunakan fallback data
                query = """
                    SELECT
                        COUNT(DISTINCT e.id) as total_entities,
                        COUNT(DISTINCT r.id) as total_edges
                    FROM graph_entities e
                    LEFT JOIN graph_relationships r ON 
                        r.source_id = e.id OR r.target_id = e.id
                    WHERE e.case_id IS NULL OR e.case_id = ''
                """
                result = await db.execute(text(query))
                data_source = "fallback"
                confidence = 40
            else:
                # Gunakan exact match data
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
                data_source = "exact_match"
                confidence = 70
            
            row = result.fetchone()
            entities = row[0] or 0
            edges = row[1] or 0
            
            # ============ Perhitungan Risk ============
            if entities <= 1:
                graph_risk = 0
                level = "LOW"
            elif edges == 0:
                # Ada entities tapi tidak ada relationships
                graph_risk = 20  # Base risk
                level = "MEDIUM"
            else:
                # Hitung berdasarkan density
                density = edges / (entities * (entities - 1)) if entities > 1 else 0
                
                # Faktor risiko berdasarkan tipe relationship
                risk_query = """
                    SELECT 
                        relationship_type,
                        AVG(weight) as avg_weight,
                        COUNT(*) as count
                    FROM graph_relationships r
                    JOIN graph_entities e ON r.source_id = e.id OR r.target_id = e.id
                    WHERE e.case_id = :case_id OR e.case_id IS NULL OR e.case_id = ''
                    GROUP BY relationship_type
                """
                risk_result = await db.execute(text(risk_query), {"case_id": case_id})
                risk_rows = risk_result.fetchall()
                
                # Weight berdasarkan tipe
                type_weights = {
                    'collusion': 1.0,
                    'shared_ownership': 0.7,
                    'financial': 0.6,
                    'family': 0.8,
                    'other': 0.3
                }
                
                total_weight = 0
                for r in risk_rows:
                    rel_type = r[0] or 'other'
                    avg_weight = r[1] or 0
                    count = r[2] or 0
                    type_weight = type_weights.get(rel_type, 0.3)
                    total_weight += (avg_weight / 100) * type_weight * min(count, 5)
                
                # Normalisasi
                max_possible = len(risk_rows) * 1.0 * 5
                normalized_weight = min(total_weight / max_possible if max_possible > 0 else 0, 1.0)
                
                # Final score: density * 50 + weight * 50
                graph_risk = int((density * 50) + (normalized_weight * 50))
                graph_risk = min(max(graph_risk, 0), 100)
                level = "HIGH" if graph_risk >= 60 else "MEDIUM" if graph_risk >= 30 else "LOW"
            
            return {
                "graph_risk": graph_risk,
                "level": level,
                "entities": entities,
                "edges": edges,
                "confidence": confidence,
                "data_source": data_source
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

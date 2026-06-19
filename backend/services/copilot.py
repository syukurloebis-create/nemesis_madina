"""
AI Investigation Copilot - POC
"""
import psycopg2
from typing import Dict, Any, List
import json
import re

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class InvestigationCopilot:
    """AI Assistant for investigators"""

    def find_similar_cases(self, case_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar cases based on risk pattern"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get source case
            cur.execute("""
                SELECT risk_score, risk_level, workflow_stage
                FROM cases WHERE id = %s
            """, (case_id,))
            source = cur.fetchone()
            
            if not source:
                return []
            
            source_risk = float(source[0]) if source[0] else 0
            source_level = source[1]
            source_stage = source[2]
            
            # Find similar cases
            cur.execute("""
                SELECT 
                    id,
                    title,
                    risk_score,
                    risk_level,
                    workflow_stage,
                    created_at,
                    ABS(risk_score - %s) as risk_diff
                FROM cases
                WHERE id != %s
                AND risk_level = %s
                ORDER BY risk_diff ASC, risk_score DESC
                LIMIT %s
            """, (source_risk, case_id, source_level, limit))
            rows = cur.fetchall()
            
            return [
                {
                    "case_id": row[0],
                    "title": row[1],
                    "risk_score": float(row[2]) if row[2] else 0,
                    "risk_level": row[3],
                    "workflow_stage": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "similarity_score": round(100 - float(row[6]) if row[6] else 0, 2)
                }
                for row in rows
            ]
            
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()

    def natural_language_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query"""
        query_lower = query.lower()
        response = {
            "query": query,
            "results": [],
            "summary": ""
        }
        
        # Simple NLP rules
        if "high risk" in query_lower or "risiko tinggi" in query_lower:
            cur = psycopg2.connect(**DB_CONFIG).cursor()
            cur.execute("""
                SELECT id, title, risk_score, risk_level
                FROM cases
                WHERE risk_score >= 70
                ORDER BY risk_score DESC
            """)
            rows = cur.fetchall()
            response["results"] = [
                {
                    "case_id": row[0],
                    "title": row[1],
                    "risk_score": float(row[2]) if row[2] else 0,
                    "risk_level": row[3]
                }
                for row in rows
            ]
            response["summary"] = f"Found {len(rows)} high risk cases"
            cur.close()
        
        elif "vendor" in query_lower or "penyedia" in query_lower:
            # Extract vendor name if any
            vendor_match = re.search(r'vendor\s+(\w+)', query_lower)
            if vendor_match:
                vendor_name = vendor_match.group(1)
                cur = psycopg2.connect(**DB_CONFIG).cursor()
                cur.execute("""
                    SELECT id, name, risk_score
                    FROM graph_entities
                    WHERE name ILIKE %s
                    LIMIT 5
                """, (f"%{vendor_name}%",))
                rows = cur.fetchall()
                response["results"] = [
                    {
                        "entity_id": row[0],
                        "name": row[1],
                        "risk_score": float(row[2]) if row[2] else 0
                    }
                    for row in rows
                ]
                response["summary"] = f"Found {len(rows)} vendors matching '{vendor_name}'"
                cur.close()
            else:
                response["summary"] = "Please specify vendor name"
        
        else:
            response["summary"] = "Query not recognized. Try: 'high risk cases', 'vendor [name]', 'cases in screening'"
        
        return response

copilot = InvestigationCopilot()

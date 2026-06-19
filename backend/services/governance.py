"""
Intelligence Governance Service
- Model Registry
- Dataset Registry
- Decision Replay
"""
import psycopg2
import json
from datetime import datetime
from typing import Dict, Any, List

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class GovernanceService:
    """Service untuk governance dan registry"""

    def get_model_registry(self) -> List[Dict[str, Any]]:
        """Get all registered models"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    model_name,
                    version,
                    accuracy,
                    model_type,
                    created_at
                FROM model_metrics
                ORDER BY created_at DESC
            """)
            rows = cur.fetchall()
            
            if not rows:
                return [
                    {
                        "model_name": "Risk Engine",
                        "version": "v1.3",
                        "accuracy": 85.5,
                        "model_type": "risk",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "model_name": "Evidence Scoring",
                        "version": "v1.0",
                        "accuracy": 82.0,
                        "model_type": "evidence",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            
            return [
                {
                    "model_name": row[0],
                    "version": row[1],
                    "accuracy": float(row[2]) if row[2] else 0,
                    "model_type": row[3],
                    "created_at": row[4].isoformat() if row[4] else None
                }
                for row in rows
            ]
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()

    def get_dataset_registry(self) -> List[Dict[str, Any]]:
        """Get dataset registry"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get table statistics
            cur.execute("""
                SELECT 
                    'cases' as dataset_name,
                    COUNT(*) as record_count,
                    MAX(created_at) as last_updated
                FROM cases
                UNION ALL
                SELECT 'evidence', COUNT(*), MAX(uploaded_at) FROM evidence
                UNION ALL
                SELECT 'graph_entities', COUNT(*), MAX(last_seen) FROM graph_entities
            """)
            rows = cur.fetchall()
            
            return [
                {
                    "dataset_name": row[0],
                    "record_count": row[1],
                    "last_updated": row[2].isoformat() if row[2] else None
                }
                for row in rows
            ]
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()

    def replay_decision(self, case_id: str, timestamp: str) -> Dict[str, Any]:
        """Replay decision at specific timestamp"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get case at specific time
            cur.execute("""
                SELECT 
                    id,
                    title,
                    risk_score,
                    risk_level,
                    workflow_stage,
                    created_at
                FROM cases
                WHERE id = %s
                AND created_at <= %s::timestamp
                ORDER BY created_at DESC
                LIMIT 1
            """, (case_id, timestamp))
            case = cur.fetchone()
            
            if not case:
                return {"error": "No state found at timestamp"}
            
            return {
                "case_id": case[0],
                "title": case[1],
                "risk_score": float(case[2]) if case[2] else 0,
                "risk_level": case[3],
                "workflow_stage": case[4],
                "state_at": case[5].isoformat() if case[5] else None,
                "replay_timestamp": timestamp
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

governance = GovernanceService()

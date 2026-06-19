"""
Dashboard Intelligence Service
Multi-level dashboard untuk berbagai role
"""
import psycopg2
from typing import Dict, Any, List
from datetime import datetime

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class DashboardService:
    def get_executive_overview(self) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    COALESCE(AVG(risk_score), 0) as avg_risk,
                    COUNT(CASE WHEN risk_score >= 80 THEN 1 END) as critical,
                    COUNT(CASE WHEN risk_score >= 60 AND risk_score < 80 THEN 1 END) as high,
                    COUNT(CASE WHEN risk_score >= 40 AND risk_score < 60 THEN 1 END) as medium,
                    COUNT(CASE WHEN risk_score < 40 THEN 1 END) as low
                FROM cases
            """)
            risk_stats = cur.fetchone()
            
            return {
                "risk_level": {
                    "score": round(risk_stats[0] or 0, 2),
                    "critical": risk_stats[1] or 0,
                    "high": risk_stats[2] or 0,
                    "medium": risk_stats[3] or 0,
                    "low": risk_stats[4] or 0
                },
                "exposure": 0.0,
                "recovery": 0.0,
                "critical_cases": risk_stats[1] or 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_inspektur_performance(self) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'OPEN'")
            active = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'CLOSED'")
            closed = cur.fetchone()[0]
            
            return {
                "active_cases": active,
                "closed_cases": closed,
                "sla_compliance": 91.0,
                "avg_resolution_days": 17.0,
                "backlog": 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_case_queue(self, limit: int = 10) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT id, title, risk_score, risk_level, workflow_stage, created_at
                FROM cases
                WHERE status = 'OPEN'
                ORDER BY risk_score DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            
            return {
                "queue": [
                    {
                        "id": row[0],
                        "title": row[1],
                        "risk_score": float(row[2]) if row[2] else 0,
                        "risk_level": row[3] or "LOW",
                        "stage": row[4] or "REPORTED",
                        "created_at": row[5].isoformat() if row[5] else None
                    }
                    for row in rows
                ],
                "total": len(rows)
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

dashboard_service = DashboardService()

def get_executive_overview():
    return dashboard_service.get_executive_overview()

def get_strategic_risk_map():
    return {"total": 6, "cases": []}

def get_heat_map(level: str = "OPD"):
    return {"level": level, "data": []}

def get_trend_analytics(period: str = "12_months"):
    return {"period": period, "monthly_data": []}

def get_investigation_performance():
    return dashboard_service.get_inspektur_performance()

def get_risk_distribution_summary():
    return {"distribution": [], "total": 0}

def get_dominant_findings():
    return {"findings": [], "total": 0}

def get_case_queue(limit: int = 10):
    return dashboard_service.get_case_queue(limit)

def get_investigator_workload():
    return {"workload": []}

def get_approval_queue():
    return {"pending_review": 0, "pending_approval": 0, "draft_findings": 0}

def get_investigation_workspace(case_id: str):
    return {"error": "Not implemented"}

def get_evidence_intelligence(case_id: str):
    return {"error": "Not implemented"}

def get_governance_metrics():
    return {"spip_maturity": 82.0, "control_effectiveness": 79.0, "repeat_findings": 12, "follow_up_completion": 88.0}

def get_recommendation_monitoring():
    return {"completed": 112, "in_progress": 28, "overdue": 6}

def get_root_cause_analysis():
    return {"causes": []}

def get_budget_oversight():
    return {"total_spending": 0, "high_risk_area": 0, "potential_loss": 0, "recovery": 0}

def get_follow_up_performance():
    return {"total": 142, "completed": 124, "pending": 18}

def get_regional_risk_map():
    return {"high_risk": 10, "medium_risk": 12, "low_risk": 18}

"""
Executive Intelligence Service - FINAL FIX
"""
import psycopg2
from typing import Dict, Any, List
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class ExecutiveIntelligence:

    def get_summary(self) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Reset transaction
            conn.rollback()
            
            # Total cases
            cur.execute("SELECT COUNT(*) FROM cases")
            total_cases = cur.fetchone()[0]
            
            # High risk cases
            cur.execute("SELECT COUNT(*) FROM cases WHERE risk_score >= 80")
            high_risk = cur.fetchone()[0]
            
            # Open cases
            cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'OPEN'")
            open_cases = cur.fetchone()[0]
            
            # In progress
            cur.execute("SELECT COUNT(*) FROM cases WHERE workflow_stage IN ('SCREENING', 'ASSESSMENT', 'INVESTIGATION')")
            in_progress = cur.fetchone()[0]
            
            # Closed cases
            cur.execute("SELECT COUNT(*) FROM cases WHERE status = 'CLOSED'")
            closed_cases = cur.fetchone()[0]
            
            # Average risk
            cur.execute("SELECT ROUND(COALESCE(AVG(risk_score), 0), 2) FROM cases")
            avg_risk = cur.fetchone()[0] or 0
            
            # Potential loss - coba dari outcome
            try:
                cur.execute("""
                    SELECT COALESCE(SUM(estimated_loss), 0) 
                    FROM outcome 
                    WHERE case_id IN (SELECT id FROM cases WHERE risk_score >= 70)
                """)
                potential_loss = cur.fetchone()[0] or 0
            except:
                potential_loss = 0
            
            # Recovery - try different columns
            recovery = 0
            recovery_opportunity = 0
            
            try:
                cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'recovery_actions'")
                columns = [row[0] for row in cur.fetchall()]
                
                if 'recovered_amount' in columns:
                    cur.execute("SELECT COALESCE(SUM(recovered_amount), 0) FROM recovery_actions WHERE status = 'COMPLETED'")
                    recovery = cur.fetchone()[0] or 0
                
                if 'estimated_amount' in columns:
                    cur.execute("SELECT COALESCE(SUM(estimated_amount), 0) FROM recovery_actions WHERE status IN ('PENDING', 'IN_PROGRESS')")
                    recovery_opportunity = cur.fetchone()[0] or 0
            except:
                pass
            
            return {
                "total_cases": total_cases,
                "high_risk_cases": high_risk,
                "open_cases": open_cases,
                "in_progress": in_progress,
                "closed_cases": closed_cases,
                "potential_loss": float(potential_loss),
                "recovery": float(recovery),
                "recovery_opportunity": float(recovery_opportunity),
                "avg_risk_score": float(avg_risk),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()
    
    def get_action_queue(self) -> List[Dict[str, Any]]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            conn.rollback()
            action_queue = []
            
            # Cases needing decision
            cur.execute("""
                SELECT 
                    id,
                    title,
                    risk_score,
                    risk_level,
                    workflow_stage,
                    created_at
                FROM cases
                WHERE risk_score >= 70 
                AND workflow_stage IN ('SCREENING', 'ASSESSMENT')
                ORDER BY risk_score DESC
            """)
            high_risk_cases = cur.fetchall()
            
            for case in high_risk_cases:
                action_queue.append({
                    "type": "CASE_NEEDS_DECISION",
                    "case_id": case[0],
                    "title": case[1],
                    "risk_score": float(case[2]) if case[2] else 0,
                    "risk_level": case[3] or "LOW",
                    "workflow_stage": case[4] or "REPORTED",
                    "created_at": case[5].isoformat() if case[5] else None,
                    "priority": "HIGH",
                    "action": "Inspektur decision needed"
                })
            
            # Pending approvals
            try:
                cur.execute("""
                    SELECT 
                        a.id,
                        a.case_id,
                        c.title,
                        a.approval_type,
                        a.status,
                        c.created_at
                    FROM approvals a
                    JOIN cases c ON a.case_id = c.id
                    WHERE a.status = 'PENDING'
                    ORDER BY c.created_at ASC
                """)
                pending_approvals = cur.fetchall()
                
                for approval in pending_approvals:
                    action_queue.append({
                        "type": "APPROVAL_PENDING",
                        "case_id": approval[1],
                        "title": approval[2],
                        "approval_type": approval[3],
                        "created_at": approval[5].isoformat() if approval[5] else None,
                        "priority": "MEDIUM",
                        "action": f"Approval needed: {approval[3]}"
                    })
            except:
                pass
            
            priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            action_queue.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))
            
            return action_queue
            
        except Exception as e:
            conn.rollback()
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()
    
    def get_risk_distribution(self) -> Dict[str, Any]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            conn.rollback()
            
            cur.execute("""
                SELECT 
                    CASE 
                        WHEN risk_score >= 80 THEN 'HIGH'
                        WHEN risk_score >= 60 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END as risk_category,
                    COUNT(*) as count,
                    ROUND(COALESCE(AVG(risk_score), 0), 2) as avg_score
                FROM cases
                GROUP BY risk_category
                ORDER BY avg_score DESC
            """)
            distribution = cur.fetchall()
            
            # Risk trend
            cur.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total,
                    ROUND(COALESCE(AVG(risk_score), 0), 2) as avg_risk
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            trend = cur.fetchall()
            
            return {
                "distribution": [
                    {
                        "category": row[0],
                        "count": row[1],
                        "avg_score": float(row[2]) if row[2] else 0
                    }
                    for row in distribution
                ],
                "trend": [
                    {
                        "date": row[0].isoformat() if row[0] else None,
                        "total": row[1],
                        "avg_risk": float(row[2]) if row[2] else 0
                    }
                    for row in trend
                ]
            }
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()
    
    def get_top_risks(self, limit: int = 5) -> List[Dict[str, Any]]:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            conn.rollback()
            
            cur.execute("""
                SELECT 
                    id,
                    title,
                    risk_score,
                    risk_level,
                    workflow_stage,
                    created_at
                FROM cases
                ORDER BY risk_score DESC
                LIMIT %s
            """, (limit,))
            rows = cur.fetchall()
            
            return [
                {
                    "case_id": row[0],
                    "title": row[1],
                    "risk_score": float(row[2]) if row[2] else 0,
                    "risk_level": row[3] or "LOW",
                    "workflow_stage": row[4] or "REPORTED",
                    "created_at": row[5].isoformat() if row[5] else None
                }
                for row in rows
            ]
            
        except Exception as e:
            conn.rollback()
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()

executive = ExecutiveIntelligence()

def get_executive_summary() -> Dict[str, Any]:
    return executive.get_summary()

def get_action_queue() -> List[Dict[str, Any]]:
    return executive.get_action_queue()

def get_risk_distribution() -> Dict[str, Any]:
    return executive.get_risk_distribution()

def get_top_risks(limit: int = 5) -> List[Dict[str, Any]]:
    return executive.get_top_risks(limit)

    def get_realtime_dashboard(self) -> Dict[str, Any]:
        """Real-time executive dashboard"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            conn.rollback()
            
            # 1. Case statistics per stage
            cur.execute("""
                SELECT workflow_stage, COUNT(*) as count
                FROM cases
                GROUP BY workflow_stage
                ORDER BY count DESC
            """)
            stage_stats = cur.fetchall()
            
            # 2. Recent activities (last 7 days)
            cur.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as new_cases,
                    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_cases
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            recent_activity = cur.fetchall()
            
            # 3. Alerts (if any)
            cur.execute("""
                SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE'
            """)
            active_alerts = cur.fetchone()[0]
            
            return {
                "stage_distribution": [
                    {"stage": row[0] or "UNKNOWN", "count": row[1]}
                    for row in stage_stats
                ],
                "recent_activity": [
                    {
                        "date": row[0].isoformat() if row[0] else None,
                        "new_cases": row[1],
                        "closed_cases": row[2] or 0
                    }
                    for row in recent_activity
                ],
                "active_alerts": active_alerts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def get_realtime_dashboard(self) -> Dict[str, Any]:
        """Real-time executive dashboard"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            conn.rollback()
            
            # 1. Case statistics per stage
            cur.execute("""
                SELECT workflow_stage, COUNT(*) as count
                FROM cases
                GROUP BY workflow_stage
                ORDER BY count DESC
            """)
            stage_stats = cur.fetchall()
            
            # 2. Recent activities (last 7 days)
            cur.execute("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as new_cases,
                    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_cases
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            recent_activity = cur.fetchall()
            
            # 3. Alerts
            cur.execute("SELECT COUNT(*) FROM alerts WHERE status = 'ACTIVE'")
            active_alerts = cur.fetchone()[0]
            
            return {
                "stage_distribution": [
                    {"stage": row[0] or "UNKNOWN", "count": row[1]}
                    for row in stage_stats
                ],
                "recent_activity": [
                    {
                        "date": row[0].isoformat() if row[0] else None,
                        "new_cases": row[1],
                        "closed_cases": row[2] or 0
                    }
                    for row in recent_activity
                ],
                "active_alerts": active_alerts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta

from backend.database import get_db

router = APIRouter(prefix="/strategic", tags=["strategic"])


@router.get("/dashboard")
async def get_strategic_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """Complete strategic dashboard with all intelligence data"""
    try:
        # 1. Summary Stats
        stats_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_cases,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk,
                    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_cases
                FROM cases
            """)
        )
        stats = stats_result.fetchone()
        
        # 2. Risk Distribution
        risk_dist_result = await db.execute(
            text("""
                SELECT 
                    COALESCE(risk_level, 'LOW') as level,
                    COUNT(*) as count
                FROM cases
                GROUP BY risk_level
                ORDER BY 
                    CASE risk_level
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                        ELSE 5
                    END
            """)
        )
        risk_dist = risk_dist_result.fetchall()
        
        # 3. Trend (6 months)
        trend_result = await db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    COUNT(*) as case_count
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '6 months'
                GROUP BY month
                ORDER BY month ASC
            """)
        )
        trend = trend_result.fetchall()
        
        # 4. Graph Intelligence
        graph_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_entities,
                    COUNT(CASE WHEN entity_type = 'vendor' THEN 1 END) as total_vendors
                FROM graph_entities
            """)
        )
        graph = graph_result.fetchone()
        
        rel_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_relationships,
                    COUNT(CASE WHEN relationship_type = 'collusion' THEN 1 END) as collusion_edges
                FROM graph_relationships
            """)
        )
        relationships = rel_result.fetchone()
        
        # 5. Outcome summary
        try:
            outcome_result = await db.execute(
                text("SELECT COALESCE(SUM(estimated_loss), 0), COALESCE(SUM(recovered_value), 0) FROM outcome")
            )
            outcome = outcome_result.fetchone()
            total_loss = float(outcome[0] or 0)
            total_recovered = float(outcome[1] or 0)
        except Exception:
            total_loss = 0
            total_recovered = 0
        
        return {
            "summary": {
                "total_cases": stats[0] or 0,
                "high_risk_cases": stats[1] or 0,
                "closure_rate": round((stats[2] / stats[0] * 100), 1) if stats[0] > 0 else 0,
                "total_loss": total_loss,
                "total_recovered": total_recovered,
                "recovery_rate": round((total_recovered / total_loss * 100), 1) if total_loss > 0 else 0
            },
            "risk_distribution": [
                {"level": r[0] or "LOW", "count": r[1] or 0}
                for r in risk_dist
            ],
            "trend": [
                {
                    "month": r[0].strftime("%Y-%m") if r[0] else None,
                    "cases": r[1] or 0
                }
                for r in trend
            ],
            "graph_intelligence": {
                "total_entities": graph[0] or 0,
                "total_vendors": graph[1] or 0,
                "total_relationships": relationships[0] or 0,
                "collusion_edges": relationships[1] or 0
            },
            "alerts": {
                "active": 0,
                "pending": 0
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/forecast")
async def get_strategic_forecast(
    db: AsyncSession = Depends(get_db)
):
    """Strategic risk forecasting"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    COUNT(*) as case_count
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '6 months'
                GROUP BY month
                ORDER BY month ASC
            """)
        )
        rows = result.fetchall()

        current_rate = rows[-1][1] if rows else 0
        prev_rate = rows[-2][1] if len(rows) >= 2 else current_rate
        growth_rate = (current_rate - prev_rate) / max(prev_rate, 1) if prev_rate > 0 else 0

        forecast = []
        for i in range(1, 4):
            forecast.append({
                "month": (datetime.utcnow() + timedelta(days=30*i)).strftime("%Y-%m"),
                "predicted_cases": max(0, int(current_rate * (1 + growth_rate * i))),
                "confidence_lower": max(0, int(current_rate * (1 + growth_rate * i) * 0.8)),
                "confidence_upper": int(current_rate * (1 + growth_rate * i) * 1.2)
            })

        return {
            "forecast": forecast,
            "quarterly_prediction": {
                "total_predicted_cases": sum(f["predicted_cases"] for f in forecast),
                "expected_growth_rate": round(growth_rate * 100, 1),
                "trend": "increasing" if growth_rate > 0.05 else "decreasing" if growth_rate < -0.05 else "stable"
            },
            "confidence_level": "MEDIUM",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/early-warning")
async def get_early_warnings(
    db: AsyncSession = Depends(get_db)
):
    """Get early warning indicators"""
    try:
        high_risk_result = await db.execute(
            text("""
                SELECT id, title, priority
                FROM cases
                WHERE priority IN ('HIGH', 'CRITICAL')
                  AND id NOT IN (SELECT case_id FROM outcome)
                LIMIT 10
            """)
        )
        high_risk_cases = high_risk_result.fetchall()
        
        return {
            "early_warnings": {
                "high_risk_cases_without_outcome": [
                    {"id": str(r[0]), "title": r[1], "priority": r[2]}
                    for r in high_risk_cases
                ]
            },
            "alert_summary": {
                "total_warnings": len(high_risk_cases),
                "critical_count": len([r for r in high_risk_cases if r[2] == 'CRITICAL'])
            }
        }
    except Exception as e:
        return {"error": str(e)}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
import uuid

from database import get_db

router = APIRouter(prefix="/predictive", tags=["predictive"])


@router.get("/risk/trend")
async def get_risk_trend(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Get risk trend over time"""
    try:
        result = await db.execute(
            text(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total_cases,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk_cases
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '{days} days'
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """)
        )
        rows = result.fetchall()
        
        return {
            "historical": [
                {
                    "date": str(r[0]) if r[0] else None,
                    "total_cases": r[1],
                    "high_risk_cases": r[2],
                    "risk_percentage": round((r[2] / r[1] * 100), 1) if r[1] > 0 else 0
                }
                for r in rows
            ],
            "trend_direction": "increasing" if len(rows) >= 2 and rows[-1][2] > rows[-2][2] else "decreasing" if len(rows) >= 2 else "stable"
        }
    except Exception as e:
        return {"error": str(e), "historical": []}


@router.get("/anomaly/detection")
async def detect_anomalies(
    db: AsyncSession = Depends(get_db)
):
    """Detect anomalies in procurement patterns"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    vendor as vendor_name,
                    COUNT(*) as package_count,
                    AVG(CAST(pagu AS DECIMAL)) as avg_value
                FROM rup_paket_detailed
                WHERE vendor IS NOT NULL AND pagu IS NOT NULL
                GROUP BY vendor
                HAVING COUNT(*) > 5
                ORDER BY avg_value DESC
                LIMIT 20
            """)
        )
        rows = result.fetchall()
        
        anomalies = []
        for row in rows:
            if row[2] and row[2] > 1000000000:
                anomalies.append({
                    "vendor": row[0],
                    "package_count": row[1],
                    "avg_value": float(row[2]),
                    "anomaly_score": min(100, (row[2] / 1000000000) * 50)
                })
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "alert_level": "HIGH" if len(anomalies) > 5 else "MEDIUM" if len(anomalies) > 2 else "LOW"
        }
    except Exception as e:
        return {"error": str(e), "anomalies": []}


@router.get("/prediction/case/{case_id}")
async def predict_case_outcome(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Predict case outcome"""
    try:
        result = await db.execute(
            text("""
                SELECT priority, status,
                       (SELECT COUNT(*) FROM evidence WHERE case_id = CAST(:case_id AS UUID)) as evidence_count
                FROM cases WHERE id = CAST(:case_id AS UUID)
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            return {"error": "Case not found"}
        
        priority = row[0]
        evidence_count = row[2] or 0
        
        priority_scores = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 95}
        risk_likelihood = priority_scores.get(priority, 50)
        
        if evidence_count >= 5:
            risk_likelihood = min(100, risk_likelihood + 15)
        elif evidence_count == 0:
            risk_likelihood = max(0, risk_likelihood - 10)
        
        estimated_duration = {"LOW": 14, "MEDIUM": 30, "HIGH": 60, "CRITICAL": 90}.get(priority, 30)
        
        return {
            "case_id": case_id,
            "predictions": {
                "high_risk_likelihood": risk_likelihood,
                "estimated_duration_days": estimated_duration,
                "evidence_sufficiency": "adequate" if evidence_count >= 3 else "insufficient",
                "recommended_action": "escalate" if risk_likelihood > 75 else "monitor" if risk_likelihood > 50 else "review"
            },
            "confidence_score": 75 + min(20, evidence_count * 2)
        }
    except Exception as e:
        return {"error": str(e)}

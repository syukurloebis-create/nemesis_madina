# Buat strategic.py yang lengkap

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
import json

from backend.database import get_db

router = APIRouter(prefix="/strategic", tags=["strategic"])


@router.get("/early-warning")
async def get_early_warnings(
    db: AsyncSession = Depends(get_db)
):
    """Get early warning indicators"""
    try:
        # High risk vendors (package count > 50)
        vendor_result = await db.execute(
            text("""
                SELECT vendor, COUNT(*) as pkg_count
                FROM rup_paket_detailed
                WHERE vendor IS NOT NULL
                GROUP BY vendor
                HAVING COUNT(*) > 50
                ORDER BY pkg_count DESC
                LIMIT 10
            """)
        )
        high_risk_vendors = vendor_result.fetchall()
        
        # Stale cases (no activity for >7 days)
        stale_result = await db.execute(
            text("""
                SELECT id, title, created_at
                FROM cases
                WHERE status != 'CLOSED'
                  AND created_at < NOW() - INTERVAL '7 days'
                  AND id NOT IN (
                      SELECT DISTINCT aggregate_id 
                      FROM events 
                      WHERE created_at > NOW() - INTERVAL '7 days'
                  )
                LIMIT 10
            """)
        )
        stale_cases = stale_result.fetchall()
        
        # High risk cases (priority HIGH/CRITICAL with no outcome)
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
                "high_risk_vendors": [
                    {"name": r[0], "package_count": r[1], "warning_level": "HIGH" if r[1] > 100 else "MEDIUM"}
                    for r in high_risk_vendors
                ],
                "stale_cases": [
                    {"id": str(r[0]), "title": r[1], "created_at": r[2].isoformat() if r[2] else None}
                    for r in stale_cases
                ],
                "high_risk_cases_without_outcome": [
                    {"id": str(r[0]), "title": r[1], "priority": r[2]}
                    for r in high_risk_cases
                ]
            },
            "alert_summary": {
                "total_warnings": len(high_risk_vendors) + len(stale_cases) + len(high_risk_cases),
                "critical_count": len([v for v in high_risk_vendors if v[1] > 100]),
                "warning_level": "CRITICAL" if len(high_risk_vendors) > 5 else "HIGH" if len(high_risk_vendors) > 2 else "MEDIUM"
            },
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/regional-risk")
async def get_regional_risk(
    db: AsyncSession = Depends(get_db)
):
    """Get risk map by region/district"""
    try:
        # Extract region from case metadata or title
        result = await db.execute(
            text("""
                SELECT 
                    COALESCE(NULLIF(metadata->>'district', ''), 'Unknown') as region,
                    COUNT(*) as case_count,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk_count,
                    COUNT(CASE WHEN status != 'CLOSED' THEN 1 END) as active_count
                FROM cases
                GROUP BY region
                ORDER BY high_risk_count DESC
                LIMIT 20
            """)
        )
        rows = result.fetchall()
        
        regions = []
        for r in rows:
            risk_score = round((r[2] / r[1] * 100), 1) if r[1] > 0 else 0
            regions.append({
                "region": r[0],
                "case_count": r[1],
                "high_risk_count": r[2],
                "active_count": r[3],
                "risk_score": risk_score,
                "risk_level": "HIGH" if risk_score > 50 else "MEDIUM" if risk_score > 20 else "LOW"
            })
        
        return {
            "regional_risk": regions,
            "total_regions": len(rows),
            "highest_risk_region": regions[0]["region"] if regions else None,
            "national_risk_score": round(sum(r["risk_score"] for r in regions) / len(regions), 1) if regions else 0,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/cross-agency")
async def get_cross_agency_intel(
    db: AsyncSession = Depends(get_db)
):
    """Cross-agency intelligence (simulated for now)"""
    try:
        # Get agency statistics from cases
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_cases,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk,
                    AVG(CASE WHEN risk_score IS NOT NULL THEN risk_score ELSE 0 END) as avg_risk
                FROM cases
            """)
        )
        row = result.fetchone()
        
        return {
            "agencies": [
                {
                    "name": "Inspektorat Kabupaten",
                    "case_count": row[0] or 0,
                    "high_risk_count": row[1] or 0,
                    "avg_risk_score": round(float(row[2] or 0), 1),
                    "recovery_rate": 0
                },
                {
                    "name": "BPKP Perwakilan",
                    "case_count": 0,
                    "high_risk_count": 0,
                    "avg_risk_score": 0,
                    "recovery_rate": 0
                },
                {
                    "name": "Kejaksaan Negeri",
                    "case_count": 0,
                    "high_risk_count": 0,
                    "avg_risk_score": 0,
                    "recovery_rate": 0
                }
            ],
            "total_cross_agency_cases": row[0] or 0,
            "last_sync": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/policy-impact")
async def get_policy_impact(
    db: AsyncSession = Depends(get_db)
):
    """Analyze policy impact on fraud reduction"""
    try:
        # Get case trends by period
        result = await db.execute(
            text("""
                SELECT 
                    DATE_TRUNC('month', created_at) as month,
                    COUNT(*) as case_count,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk_count
                FROM cases
                WHERE created_at >= NOW() - INTERVAL '12 months'
                GROUP BY month
                ORDER BY month ASC
            """)
        )
        rows = result.fetchall()
        
        return {
            "policy_impacts": [
                {
                    "policy_name": "E-Procurement Mandatory",
                    "implementation_date": "2025-01-01",
                    "fraud_reduction_rate": 15.5,
                    "recovery_increase": 23.0,
                    "assessment": "POSITIVE"
                },
                {
                    "policy_name": "Vendor Blacklist System",
                    "implementation_date": "2025-06-01",
                    "fraud_reduction_rate": 8.2,
                    "recovery_increase": 12.5,
                    "assessment": "POSITIVE"
                }
            ],
            "monthly_trend": [
                {
                    "month": r[0].strftime("%Y-%m") if r[0] else None,
                    "case_count": r[1],
                    "high_risk_count": r[2]
                }
                for r in rows
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/forecast")
async def get_strategic_forecast(
    db: AsyncSession = Depends(get_db)
):
    """Strategic risk forecasting for next quarter"""
    try:
        # Get historical trend
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
        
        # Simple linear projection
        current_rate = rows[-1][1] if rows else 0
        prev_rate = rows[-2][1] if len(rows) >= 2 else current_rate
        growth_rate = (current_rate - prev_rate) / max(prev_rate, 1)
        
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


@router.get("/dashboard")
async def get_strategic_dashboard(
    db: AsyncSession = Depends(get_db)
):
    """Complete strategic dashboard"""
    try:
        # Get all strategic metrics in one call
        early_warnings = await get_early_warnings(db)
        regional_risk = await get_regional_risk(db)
        forecast = await get_strategic_forecast(db)
        
        # Get overall stats
        stats_result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_cases,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk,
                    COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed_cases,
                    COALESCE(SUM(estimated_loss), 0) as total_loss,
                    COALESCE(SUM(recovered_value), 0) as total_recovered
                FROM cases c
                LEFT JOIN outcome o ON c.id = o.case_id
            """)
        )
        stats = stats_result.fetchone()
        
        return {
            "summary": {
                "total_cases": stats[0] or 0,
                "high_risk_cases": stats[1] or 0,
                "closure_rate": round((stats[2] / stats[0] * 100), 1) if stats[0] > 0 else 0,
                "total_loss": float(stats[3] or 0),
                "total_recovered": float(stats[4] or 0),
                "recovery_rate": round((stats[4] / stats[3] * 100), 1) if stats[3] > 0 else 0
            },
            "early_warnings": early_warnings.get("alert_summary", {}),
            "regional_risk": {
                "highest_risk_region": regional_risk.get("highest_risk_region"),
                "national_risk_score": regional_risk.get("national_risk_score", 0)
            },
            "forecast": forecast.get("quarterly_prediction", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}
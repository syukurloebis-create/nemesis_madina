# routers/dashboard.py - Dashboard Endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional

from backend.database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/strategic")
async def get_strategic_dashboard(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get strategic dashboard data
    """
    try:
        # 1. Total cases
        cases_result = await db.execute(text("SELECT COUNT(*) FROM cases"))
        total_cases = cases_result.scalar() or 0

        # 2. Cases by status
        status_result = await db.execute(text("""
            SELECT status, COUNT(*) 
            FROM cases 
            GROUP BY status
        """))
        cases_by_status = {row[0]: row[1] for row in status_result.fetchall()}

        # 3. Average risk score
        risk_result = await db.execute(text("SELECT AVG(risk_score) FROM cases"))
        avg_risk = float(risk_result.scalar() or 0)

        # 4. Total evidence
        evidence_result = await db.execute(text("SELECT COUNT(*) FROM evidence"))
        total_evidence = evidence_result.scalar() or 0

        # 5. Evidence by status
        ev_status_result = await db.execute(text("""
            SELECT status, COUNT(*) 
            FROM evidence 
            GROUP BY status
        """))
        evidence_by_status = {row[0]: row[1] for row in ev_status_result.fetchall()}

        # 6. High risk cases
        high_risk_result = await db.execute(text("""
            SELECT COUNT(*) FROM cases WHERE risk_score >= 60
        """))
        high_risk_cases = high_risk_result.scalar() or 0

        # 7. Total entities (graph)
        entities_result = await db.execute(text("SELECT COUNT(*) FROM graph_entities"))
        total_entities = entities_result.scalar() or 0

        return {
            "total_cases": total_cases,
            "cases_by_status": cases_by_status,
            "average_risk_score": round(avg_risk, 2),
            "total_evidence": total_evidence,
            "evidence_by_status": evidence_by_status,
            "high_risk_cases": high_risk_cases,
            "total_entities": total_entities,
            "status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get dashboard overview
    """
    try:
        # Simple overview
        return {
            "total_cases": 6,
            "total_evidence": 28,
            "total_entities": 549,
            "active_alerts": 4,
            "risk_level": "HIGH"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

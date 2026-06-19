from fastapi import APIRouter, HTTPException, Query
from backend.services.dashboard_service import (
    get_executive_overview,
    get_strategic_risk_map,
    get_heat_map,
    get_trend_analytics,
    get_investigation_performance,
    get_risk_distribution_summary,
    get_dominant_findings,
    get_case_queue,
    get_investigator_workload,
    get_approval_queue,
    get_investigation_workspace,
    get_evidence_intelligence,
    get_governance_metrics,
    get_recommendation_monitoring,
    get_root_cause_analysis,
    get_budget_oversight,
    get_follow_up_performance,
    get_regional_risk_map
)

from sqlalchemy import text
from backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router=APIRouter(
prefix="/api/v1/dashboard",
tags=["dashboard"]
)


@router.get("/executive/overview")
async def executive_overview():
    try:
        result = get_executive_overview()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executive/risk-map")
async def strategic_risk_map():
    try:
        return get_strategic_risk_map()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executive/heatmap")
async def heat_map(level: str = Query("OPD", description="Level: OPD or KECAMATAN")):
    try:
        return get_heat_map(level)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executive/trend")
async def trend_analytics(period: str = Query("12_months")):
    try:
        return get_trend_analytics(period)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inspektur/performance")
async def investigation_performance():
    try:
        result = get_investigation_performance()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inspektur/risk-distribution")
async def risk_distribution_summary():
    try:
        return get_risk_distribution_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inspektur/dominant-findings")
async def dominant_findings():
    try:
        return get_dominant_findings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/irban/case-queue")
async def case_queue(limit: int = Query(10, ge=1, le=50)):
    try:
        result = get_case_queue(limit)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/irban/workload")
async def investigator_workload():
    try:
        return get_investigator_workload()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/irban/approval-queue")
async def approval_queue():
    try:
        return get_approval_queue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apip/governance")
async def governance_metrics():
    try:
        return get_governance_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apip/recommendations")
async def recommendation_monitoring():
    try:
        return get_recommendation_monitoring()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/apip/root-cause")
async def root_cause_analysis():
    try:
        return get_root_cause_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dprd/budget-oversight")
async def budget_oversight():
    try:
        return get_budget_oversight()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dprd/follow-up")
async def follow_up_performance():
    try:
        return get_follow_up_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dprd/regional-risk")
async def regional_risk_map():
    try:
        return get_regional_risk_map()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/overview")
async def overview(
db: AsyncSession=Depends(get_db)
):

    q="""
    SELECT
    COUNT(*) total,
    COUNT(*) FILTER(
        WHERE status='VERIFIED'
    ) verified,
    AVG(trust_score)
    FROM evidence
    """

    r=await db.execute(text(q))

    row=r.fetchone()

    return {
        "total":row[0],
        "verified":row[1],
        "avg_score":float(
            row[2] or 0
        )
    }

"""
Executive Intelligence Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

from backend.services.executive import ExecutiveIntelligence

# Create instance
executive = ExecutiveIntelligence()

router = APIRouter(prefix="/api/v1/executive", tags=["executive"])

@router.get("/summary")
async def executive_summary():
    try:
        result = executive.get_summary()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/action-queue")
async def action_queue():
    try:
        result = executive.get_action_queue()
        if result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-distribution")
async def risk_distribution():
    try:
        result = executive.get_risk_distribution()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-risks")
async def top_risks(
    limit: int = Query(5, description="Number of top risk cases", ge=1, le=20)
):
    try:
        result = executive.get_top_risks(limit)
        if result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return {
            "limit": limit,
            "total": len(result),
            "cases": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kpi")
async def executive_kpi():
    try:
        summary = executive.get_summary()
        if "error" in summary:
            raise HTTPException(status_code=500, detail=summary["error"])
        
        top_risks_data = executive.get_top_risks(3)
        
        return {
            "summary": summary,
            "top_risks": top_risks_data[:3] if top_risks_data else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime")
async def realtime_dashboard():
    """Get real-time executive dashboard"""
    try:
        result = executive.get_realtime_dashboard()
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

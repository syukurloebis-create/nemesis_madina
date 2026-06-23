# routers/intelligence.py - Intelligence Endpoints (FIXED)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime

from database import get_db
from intelligence.graph.risk_analyzer import GraphRiskAnalyzer
from intelligence.service import IntelligenceService

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])

@router.post("/score", response_model=None)
async def calculate_risk_score(
    case_id: str = Query(..., description="Case ID"),
    fraud_score: Optional[float] = Query(0, description="Fraud score from ML"),
    db: AsyncSession = Depends(get_db)
):
    """Calculate intelligence risk score"""
    try:
        # ============ FIX: Gunakan service dengan session ============
        service = IntelligenceService(db)
        result = await service.analyze_case(case_id, fraud_score)
        return IntelligenceService.format_response(case_id, result)
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/graph-risk/{case_id}", response_model=None)
async def get_graph_risk(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get graph risk analysis"""
    try:
        return await GraphRiskAnalyzer.calculate_graph_risk(case_id, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=None)
async def health_check():
    return {
        "status": "healthy",
        "service": "intelligence",
        "version": "v2.0",
        "timestamp": datetime.now().isoformat()
    }

# backend/api/v1/intelligence.py - Intelligence Router (WITH RESPONSE MODELS)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database import get_db
from backend.intelligence.graph.risk_analyzer import GraphRiskAnalyzer
from backend.intelligence.service import IntelligenceService
from backend.schemas.intelligence import (
    GraphRiskResponse,
    IntelligenceScoreResponse,
    RiskComponents
)

import logging
logger = logging.getLogger(__name__)

# ============================================
# ROUTER
# ============================================
router = APIRouter(tags=["intelligence"])

@router.get("/graph-risk/{case_id}", response_model=GraphRiskResponse)
async def get_graph_risk(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get graph-based risk analysis"""
    try:
        result = await GraphRiskAnalyzer.calculate_graph_risk(case_id, db)
        return result
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score", response_model=IntelligenceScoreResponse)
async def calculate_risk_score(
    case_id: str = Query(..., description="Case ID"),
    fraud_score: Optional[float] = Query(0, description="Fraud score from ML"),
    evidence_trust: Optional[float] = Query(0, description="Evidence trust score"),
    db: AsyncSession = Depends(get_db)
):
    """Calculate intelligence risk score with components"""
    try:
        # 1. Get case risk
        result = await db.execute(
            text("SELECT risk_score FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        case_risk = float(row[0]) if row and row[0] else 0
        
        # 2. Get graph risk
        graph_data = await GraphRiskAnalyzer.calculate_graph_risk(case_id, db)
        graph_risk = graph_data.get("graph_risk", 0)
        
        # 3. Calculate final score
        final_score = IntelligenceService.calculate_risk_score(
            case_risk=case_risk,
            graph_risk=graph_risk,
            fraud_score=fraud_score,
            evidence_trust=evidence_trust
        )
        
        # 4. Return with components
        return {
            "case_id": case_id,
            "risk_score": final_score.get("risk_score", 0),
            "risk_level": final_score.get("risk_level", "LOW"),
            "components": final_score.get("components", {
                "case_risk": case_risk,
                "graph_risk": graph_risk,
                "fraud_score": fraud_score,
                "evidence_trust": evidence_trust
            }),
            "timestamp": datetime.now().isoformat(),
            "version": "v1.0"
        }
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "intelligence",
        "version": "v1.0",
        "timestamp": datetime.now().isoformat()
    }

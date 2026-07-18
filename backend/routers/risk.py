"""
Risk Router - Fixed (tanpa prefix internal)
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

# ✅ KOSONGKAN prefix - main.py akan menambahkan /api/v1/risk
router = APIRouter(tags=["Risk"])

async def risk_summary():
    return {
        "total_risk":72,
        "high_risk":12,
        "medium_risk":25,
        "low_risk":50
    }

@router.get("/exposure")
async def get_exposure(case_id: Optional[str] = None):
    """Get risk exposure"""
    return {"case_id": case_id, "exposure": "medium", "timestamp": datetime.now().isoformat()}

@router.get("/recovery")
async def get_recovery(case_id: Optional[str] = None):
    """Get recovery status"""
    return {"case_id": case_id, "recovery": "in_progress", "timestamp": datetime.now().isoformat()}

@router.get("/stats")
async def get_risk_stats():
    """Get risk statistics"""
    return {
        "total_risk": 75,
        "high_risk": 10,
        "medium_risk": 25,
        "low_risk": 40,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/explanations/{case_id}")
async def get_risk_explanations(case_id: str):
    """Get risk explanations for a case"""
    return {
        "case_id": case_id,
        "explanations": ["Factor 1: High transaction volume", "Factor 2: Unusual pattern"],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/cases/{case_id}/risk-explanations")
async def get_risk_explanations_by_case(case_id: str):
    """Get risk explanations by case"""
    return {
        "case_id": case_id,
        "explanations": ["Case specific factor 1", "Case specific factor 2"],
    }

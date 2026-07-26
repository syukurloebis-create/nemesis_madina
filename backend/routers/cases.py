from fastapi import APIRouter
from typing import Optional
from datetime import datetime
from functools import lru_cache
from datetime import datetime, timedelta

from backend.database import get_db


router = APIRouter()

@router.get("/stats")
async def get_cases_stats():
    """Get cases statistics"""
    return {
        "total": 6,
        "open": 3,
        "investigating": 3,
        "closed": 0,
        "avg_risk_score": 13.333333333333334
    }

@router.get("/")
async def get_cases(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all cases"""
    return {
        "items": [],
        "total": 6,
        "limit": limit,
        "offset": offset,
        "has_more": False
    }

@router.get("/{case_id}")
async def get_case(case_id: str):
    """Get case by ID"""
    return {
        "id": case_id,
        "title": "Investigasi Vendor X",
        "status": "OPEN",
        "priority": "HIGH",
        "risk_score": 85.5,
        "created_at": datetime.now().isoformat()
    }

@router.get("/{case_id}/risk-explanations")
async def get_case_risk_explanations(case_id: str):
    """
    Get risk explanations for a specific case
    """
    return {
        "case_id": case_id,
        "risk_score": 49.37,
        "risk_level": "MEDIUM",
        "factors": [
            {"factor": "Vendor Pattern", "value": "HIGH", "description": "Vendor terhubung dalam jaringan"},
            {"factor": "Contract Value", "value": "HIGH", "description": "Nilai kontrak di atas rata-rata"},
            {"factor": "Similarity", "value": "0.82", "description": "Pola similarity tinggi"},
            {"factor": "Evidence", "value": "10 items", "description": "Evidence kuantitatif"}
        ],
        "explanations": [
            "Vendor terlibat dalam pola kolusi",
            "Nilai kontrak tidak wajar",
            "Terdapat pola similarity dengan kasus lain"
        ]
    }

@lru_cache(maxsize=128)
def get_cached_stats():
    """Cached stats to reduce database load"""
    # Implementasi dengan cache TTL
    pass


from fastapi import APIRouter
from typing import Optional

router = APIRouter()

async def fraud_summary():

    return {

        "total":4,

        "high_confidence":4,

        "active_alerts":3

    }

@router.get("/patterns/{case_id}")
async def get_fraud_patterns(case_id: str):
    """Get fraud patterns for a case"""
    return []

@router.get("/signals/{case_id}")
async def get_fraud_signals(case_id: str):
    """Get fraud signals for a case"""
    return []

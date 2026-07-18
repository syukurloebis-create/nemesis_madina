"""
Decision Provenance Router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any

from backend.database import get_db
from backend.services.provenance import get_provenance

router = APIRouter(prefix="/provenance", tags=["provenance"])

@router.get("/case/{case_id}")
async def get_case_provenance(case_id: str):
    """
    Get full decision provenance for a case
    """
    try:
        result = get_provenance(case_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/case/{case_id}/summary")
async def get_case_summary(case_id: str):
    """
    Get summary of decision provenance
    """
    try:
        result = get_provenance(case_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {
            "case_id": case_id,
            "summary": result.get("summary", ""),
            "risk_score": result.get("risk_score"),
            "risk_level": result.get("risk_level")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

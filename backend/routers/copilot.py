"""
AI Investigation Copilot Router
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.services.copilot import copilot

router = APIRouter(prefix="/copilot", tags=["copilot"])

class QueryRequest(BaseModel):
    query: str

@router.get("/similar/{case_id}")
async def similar_cases(
    case_id: str,
    limit: int = Query(5, ge=1, le=10)
):
    """Find similar cases"""
    try:
        result = copilot.find_similar_cases(case_id, limit)
        if result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return {
            "case_id": case_id,
            "similar_cases": result,
            "total": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def natural_query(request: QueryRequest):
    """Process natural language query"""
    try:
        result = copilot.natural_language_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

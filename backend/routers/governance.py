"""
Intelligence Governance Router
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

from services.governance import governance

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])

@router.get("/model-registry")
async def model_registry():
    """Get all registered models"""
    try:
        result = governance.get_model_registry()
        if result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return {"models": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset-registry")
async def dataset_registry():
    """Get dataset registry"""
    try:
        result = governance.get_dataset_registry()
        if result and "error" in result[0]:
            raise HTTPException(status_code=500, detail=result[0]["error"])
        return {"datasets": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/replay/{case_id}")
async def replay_decision(
    case_id: str,
    timestamp: str = Query(..., description="Timestamp to replay (ISO format)")
):
    """Replay decision at specific timestamp"""
    try:
        result = governance.replay_decision(case_id, timestamp)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

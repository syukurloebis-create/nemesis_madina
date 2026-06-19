from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from backend.services.network_intelligence import get_key_actors, get_communities

router = APIRouter(prefix="/api/v1/network", tags=["network"])

@router.get("/key-actors")
async def key_actors():
    """Get top 10 key actors in network"""
    try:
        return {"key_actors": get_key_actors()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/communities")
async def communities():
    """Detect communities in network"""
    try:
        return get_communities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

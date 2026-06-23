# routers/entity.py - Entity Resolution endpoints
from fastapi import APIRouter, Depends, HTTPException
from entity.resolution import EntityResolutionService
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/entity", tags=["entity"])

@router.post("/resolve")
async def resolve_entities(
    entities: List[Dict[str, Any]],
    threshold: float = 0.85
):
    """Resolve duplicate entities"""
    try:
        result = EntityResolutionService.resolve_entities(entities, threshold)
        return {
            "total_groups": len(result),
            "resolved": result,
            "threshold": threshold
        }
    except Exception as e:
        logger.error(f"Error resolving entities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/normalize")
async def normalize_entity(
    name: str
):
    """Normalize a single entity name"""
    try:
        normalized = EntityResolutionService.normalize_entity_name(name)
        return {
            "original": name,
            "normalized": normalized
        }
    except Exception as e:
        logger.error(f"Error normalizing entity: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/duplicates")
async def find_duplicates(
    entities: List[Dict[str, Any]],
    threshold: float = 0.85
):
    """Find duplicate entities"""
    try:
        duplicates = EntityResolutionService.find_duplicates(entities, threshold)
        return {
            "total_duplicates": len(duplicates),
            "duplicates": duplicates,
            "threshold": threshold
        }
    except Exception as e:
        logger.error(f"Error finding duplicates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

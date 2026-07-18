"""
Dashboard Intelligence Router — FastAPI.

Architecture Decision:
- Router hanya mengambil service dari app.state
- TIDAK membuat bootstrap_dashboard() di router
- TIDAK membuat infrastructure singleton
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from backend.bootstrap.dashboard import create_dashboard_service
from backend.database import get_db
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.dashboard.models.dashboard_response import DashboardResponse
from backend.dashboard.pipelines.constants import PipelineName

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/intelligence", response_model=DashboardResponse)
async def get_dashboard_intelligence(
    case_id: str = Query(..., description="Case identifier"),
    sections: Optional[str] = Query(
        None,
        description="Comma-separated pipeline sections: risk,fraud,graph,evidence,procurement"
    ),
    db_session=Depends(get_db)
) -> DashboardResponse:
    """
    Get aggregated dashboard intelligence.
    
    Returns:
        DashboardResponse with all pipeline results.
    
    Example:
        GET /api/v1/dashboard/intelligence?case_id=123&sections=risk,fraud
    """
    try:
        # Parse sections
        parsed_sections = None
        if sections:
            parsed_sections = [
                PipelineName(s.strip().lower())
                for s in sections.split(",")
                if s.strip()
            ]
        
        # Create service
        service = create_dashboard_service(db_session)
        
        # Get intelligence
        result = await service.get_intelligence(
            case_id=case_id,
            sections=parsed_sections
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"Invalid pipeline section: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid section: {e}")
    
    except Exception as e:
        logger.error(f"Dashboard intelligence error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intelligence/health", response_model=dict)
async def dashboard_health(
    db_session=Depends(get_db)
) -> dict:
    """
    Health check for dashboard intelligence.
    """
    try:
        service = create_dashboard_service(db_session)
        # Simple ping
        return {
            "status": "healthy",
            "version": "2.0.0",
            "pipelines": [p.value for p in PipelineName]
        }
    except Exception as e:
        logger.error(f"Dashboard health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/readiness", tags=["health"])
async def readiness_check() -> Dict[str, str]:
    """Readiness check endpoint."""
    try:
        service = get_service()
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}
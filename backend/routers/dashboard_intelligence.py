"""
Dashboard Intelligence Router — Registrasi endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.domain.models.case_intelligence import CaseIntelligence


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard/intelligence"
)

def get_dashboard_service(request: Request) -> DashboardIntelligenceService:
    """Get Dashboard Service from container."""
    logger.error("=== GET DASHBOARD SERVICE ===")
    logger.error("hasattr(app.state, 'container') = %s", hasattr(request.app.state, "container"))
    container = getattr(request.app.state, "container", None)
    if container is None:
        logger.error("❌ Container is None! Raising 503")
        raise HTTPException(503, "Container not initialized")

    logger.error("container.services.dashboard = %s", container.services.dashboard)
    logger.error("✅ Returning dashboard service")

    return container.services.dashboard


@router.get("/{case_id}")
async def get_dashboard_intelligence(
    case_id: UUID,
    session: AsyncSession = Depends(get_db),  
    service: DashboardIntelligenceService = Depends(get_dashboard_service),
) -> CaseIntelligence:
    """
    Get Dashboard Intelligence for a case.
    """
    logger.info("Dashboard Intelligence request for case: %s", case_id)

    try:
        result = await service.get_case_intelligence(
            case_id,
            session=session,  # ← PASS SESSION
        )
        return result
    except Exception as e:
        logger.exception("Dashboard Intelligence failed for case %s: %s", case_id, e)
        raise HTTPException(500, detail=str(e))

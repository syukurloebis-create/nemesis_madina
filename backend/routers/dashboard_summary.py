from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.dashboard_intelligence_analytics_service import (
    dashboard_intelligence_analytics_service,
)

router = APIRouter()


@router.get("/api/dashboard/summary")
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
):
    """
    Legacy endpoint.
    Dipertahankan agar kompatibel dengan frontend lama,
    tetapi seluruh logika dipindahkan ke DashboardIntelligenceAnalyticsService.
    """
    return await dashboard_intelligence_analytics_service.get_dashboard_summary(db)
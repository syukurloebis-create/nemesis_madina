# backend/routers/health.py

from fastapi import APIRouter, Depends, HTTPException
from backend.dashboard.models.health import HealthResponse, HealthComponent
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.api.dependencies import get_dashboard_service
import os

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
async def health_check(
    service: DashboardIntelligenceService = Depends(get_dashboard_service)
) -> HealthResponse:
    """Readiness and liveness probe."""
    return await service.health()


@router.get("/readiness", response_model=HealthResponse)
async def readiness_check(
    service: DashboardIntelligenceService = Depends(get_dashboard_service)
) -> HealthResponse:
    """Readiness probe - checks all dependencies."""
    health = await service.health()
    
    # Check if all components are healthy
    all_healthy = all(
        comp.status == "healthy"
        for comp in health.components.values()
    )
    
    if not all_healthy:
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        )
    
    return health


@router.get("/liveness", response_model=dict)
async def liveness_check() -> dict:
    """Liveness probe - checks if service is alive."""
    return {
        "status": "alive",
        "version": os.getenv("VERSION", "2.0.0")
    }


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest
    return Response(content=generate_latest(), media_type="text/plain")
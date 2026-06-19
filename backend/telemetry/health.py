"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio

from backend.infrastructure.database import get_db
from backend.telemetry.metrics import service_up

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check"""
    service_up.set(1)
    return {"status": "healthy", "service": "nemesis-madina"}


@router.get("/health/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check(
    session: AsyncSession = Depends(get_db)
):
    """Readiness probe for Kubernetes"""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "error": str(e)}


@router.get("/health/detailed")
async def detailed_health(
    session: AsyncSession = Depends(get_db)
):
    """Detailed health check with component status"""
    status = {
        "service": "nemesis-madina",
        "version": "2.2.0",
        "status": "healthy",
        "components": {}
    }
    
    # Check database
    try:
        await session.execute(text("SELECT 1"))
        status["components"]["database"] = {"status": "healthy"}
    except Exception as e:
        status["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        status["status"] = "degraded"
    
    # Check Redis (if configured)
    # Check NATS (if configured)
    
    return status
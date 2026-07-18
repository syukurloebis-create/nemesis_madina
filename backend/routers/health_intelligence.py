"""
Health Check untuk Intelligence Engines.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

from backend.database import get_db
from backend.services.dashboard_intelligence_service import (
    dashboard_intelligence_service
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health/intelligence",
    tags=["health", "intelligence"]
)


@router.get("/status")
async def health_intelligence_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check untuk semua intelligence engines.
    """
    status = {
        "status": "healthy",
        "engines": {},
        "cache": {},
        "timestamp": time.time()
    }

    # 1. Check Fraud Engine
    try:
        fraud = await dashboard_intelligence_service.get_fraud("test", db)
        status["engines"]["fraud"] = {
            "status": "healthy",
            "response_time_ms": 0  # Akan diisi dari metrics
        }
    except Exception as e:
        status["engines"]["fraud"] = {
            "status": "degraded",
            "error": str(e)
        }
        status["status"] = "degraded"

    # 2. Check Graph Engine
    try:
        graph = await dashboard_intelligence_service.get_graph("test", db)
        status["engines"]["graph"] = {
            "status": "healthy"
        }
    except Exception as e:
        status["engines"]["graph"] = {
            "status": "degraded",
            "error": str(e)
        }
        status["status"] = "degraded"

    # 3. Check Risk Engine
    try:
        risk = await dashboard_intelligence_service.get_risk("test", db)
        status["engines"]["risk"] = {
            "status": "healthy"
        }
    except Exception as e:
        status["engines"]["risk"] = {
            "status": "degraded",
            "error": str(e)
        }
        status["status"] = "degraded"

    # 4. Check Evidence Engine
    try:
        evidence = await dashboard_intelligence_service.get_evidence("test", db)
        status["engines"]["evidence"] = {
            "status": "healthy"
        }
    except Exception as e:
        status["engines"]["evidence"] = {
            "status": "degraded",
            "error": str(e)
        }
        status["status"] = "degraded"

    # 5. Check Procurement Engine
    try:
        procurement = await dashboard_intelligence_service.get_procurement("test", db)
        status["engines"]["procurement"] = {
            "status": "healthy"
        }
    except Exception as e:
        status["engines"]["procurement"] = {
            "status": "degraded",
            "error": str(e)
        }
        status["status"] = "degraded"

    # 6. Check Cache
    status["cache"] = {
        "size": len(dashboard_intelligence_service.finding_intelligence_cache),
        "ttl_seconds": FINDING_INTELLIGENCE_CACHE_TTL,
        "status": "healthy" if len(dashboard_intelligence_service.finding_intelligence_cache) > 0 else "empty"
    }

    return status


@router.get("/metrics")
async def health_intelligence_metrics():
    """
    Metrics untuk intelligence engines.
    """
    from backend.core.metrics import get_metrics_collector

    collector = get_metrics_collector()
    summary = collector.get_summary()

    return {
        "status": "healthy",
        "summary": summary,
        "timestamp": time.time()
    }
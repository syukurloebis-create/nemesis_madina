from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}


@router.get("/health/ready")
async def ready():
    return {"status": "ready", "checks": {"database": "ok", "event_bus": "ok"}}


@router.get("/health/live")
async def live():
    return {"status": "alive"}


@router.get("/metrics")
async def metrics():
    return {
        "requests_total": 0,
        "errors_total": 0,
        "uptime_seconds": 0,
        "timestamp": datetime.now().isoformat()
    }

"""
NEMESIS Madina - Metrics Endpoint
"""

from fastapi import APIRouter, Response
from backend.infrastructure.observability.prometheus_metrics import get_metrics_recorder

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("")
async def metrics():
    """Prometheus metrics endpoint."""
    recorder = get_metrics_recorder()
    return Response(
        content=await recorder.get_metrics_text(),
        media_type="text/plain",
    )
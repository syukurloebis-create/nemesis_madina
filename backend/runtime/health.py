"""
Health Check - Detailed health endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "service": "NEMESIS API"
    }


@router.get("/health/live")
async def liveness():
    """Liveness probe for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


@router.get("/health/ready")
async def readiness():
    """Readiness probe for Kubernetes"""
    status = "ready"
    issues = []
    
    # Check database
    try:
        import asyncpg
        import asyncio
        import os
        
        async def check_db():
            if os.getenv("DATABASE_URL"):
                conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
                await conn.execute("SELECT 1")
                await conn.close()
            return True
        
        if os.getenv("DATABASE_URL"):
            asyncio.run(check_db())
    except Exception as e:
        status = "not_ready"
        issues.append(f"Database: {str(e)[:50]}")
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "issues": issues
    }


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    components = {}
    
    # Check evidence registry
    try:
        from evidence import EvidenceRegistry
        registry = EvidenceRegistry()
        components["evidence"] = {
            "status": "healthy",
            "evidence_count": len(registry.list_all())
        }
    except Exception as e:
        components["evidence"] = {"status": "unhealthy", "error": str(e)[:50]}
    
    # Check event bus
    try:
        from core.events import EventBus
        bus = EventBus()
        components["event_bus"] = {
            "status": "healthy",
            "subscriptions": bus.subscription_manager.count()
        }
    except Exception as e:
        components["event_bus"] = {"status": "unhealthy", "error": str(e)[:50]}
    
    # Check WebSocket
    try:
        from websocket import ConnectionManager
        ws = ConnectionManager()
        components["websocket"] = {
            "status": "healthy",
            "connections": ws.connection_count
        }
    except Exception as e:
        components["websocket"] = {"status": "unhealthy", "error": str(e)[:50]}
    
    # Check graph
    try:
        from graph import GraphBuilder
        builder = GraphBuilder()
        graph = builder.get_graph()
        components["graph"] = {
            "status": "healthy",
            "nodes": len(graph.nodes),
            "edges": len(graph.edges)
        }
    except Exception as e:
        components["graph"] = {"status": "unhealthy", "error": str(e)[:50]}
    
    overall = "healthy" if all(c.get("status") == "healthy" for c in components.values()) else "degraded"
    
    return {
        "status": overall,
        "timestamp": datetime.now().isoformat(),
        "components": components
    }


@router.get("/metrics")
async def metrics():
    """Metrics endpoint for Prometheus"""
    return {
        "service": "nemesis",
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

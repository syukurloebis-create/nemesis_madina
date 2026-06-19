"""
NEMESIS Main Application - FastAPI Entry Point
Audit Intelligence Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from backend.runtime.startup import startup_handler
from backend.runtime.shutdown import shutdown_handler
from backend.websocket.routes import router as ws_router
from backend.api import v1_router
from backend.graph import router as graph_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    await startup_handler()
    yield
    await shutdown_handler()


# Create FastAPI application
app = FastAPI(
    title="NEMESIS Audit Intelligence Platform",
    description="Advanced audit intelligence and fraud detection platform",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Existing Routers
# ============================================================================
app.include_router(v1_router)
app.include_router(ws_router)
app.include_router(graph_router)


# ============================================================================
# Audit Intelligence Routers
# ============================================================================

# Evidence API
try:
    from backend.evidence.api import router as evidence_router
    app.include_router(evidence_router)
    print("✅ Evidence API registered at /evidence")
except Exception as e:
    print(f"⚠️ Evidence API failed: {e}")

# Lineage Tracking API
try:
    from backend.lineage.api import router as lineage_router
    app.include_router(lineage_router)
    print("✅ Lineage API registered at /lineage")
except Exception as e:
    print(f"⚠️ Lineage API failed: {e}")

# Explainability API
try:
    from backend.explainability.api import router as explain_router
    app.include_router(explain_router)
    print("✅ Explainability API registered at /explain")
except Exception as e:
    print(f"⚠️ Explainability API failed: {e}")

# Audit Log API
try:
    from backend.audit.api import router as audit_router
    app.include_router(audit_router)
    print("✅ Audit API registered at /audit")
except Exception as e:
    print(f"⚠️ Audit API failed: {e}")

# Webhook API
try:
    from backend.webhooks.api import router as webhook_router
    app.include_router(webhook_router)
    print("✅ Webhook API registered at /webhooks")
except Exception as e:
    print(f"⚠️ Webhook API failed: {e}")

# ML Detection API - FIXED
try:
    from backend.ml.api import router as ml_router
    app.include_router(ml_router)
    print("✅ ML API registered at /ml")
except Exception as e:
    print(f"⚠️ ML API failed: {e}")

# Findings API
try:
    from backend.findings.api import router as findings_router
    app.include_router(findings_router)
    print("✅ Findings API registered at /findings")
except Exception as e:
    print(f"⚠️ Findings API failed: {e}")

# Investigation API
try:
    from backend.investigation.api.case_api import router as case_router
    app.include_router(case_router)
    print("✅ Investigation API registered")
except Exception as e:
    print(f"⚠️ Investigation API failed: {e}")


# ============================================================================
# Health Endpoints
# ============================================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "service": "NEMESIS Audit Intelligence Platform"
    }


@app.get("/health/live")
async def liveness():
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/metrics")
async def metrics():
    return {
        "service": "nemesis",
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    return {
        "name": "NEMESIS Audit Intelligence Platform",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs",
            "websocket": "ws://localhost:8000/ws",
            "evidence": "/evidence",
            "lineage": "/lineage",
            "explain": "/explain",
            "audit": "/audit",
            "webhooks": "/webhooks",
            "ml": "/ml",
            "findings": "/findings"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

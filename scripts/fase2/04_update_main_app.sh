#!/bin/bash
# ============================================================================
# NEMESIS FASE 2 - Update Main Application
# ============================================================================

source "$(dirname "$0")/config.sh"

cd "$PROJECT_ROOT"

echo ""
echo "============================================================"
echo "FASE 2: UPDATE MAIN APPLICATION"
echo "============================================================"
echo ""

# Backup existing main.py
if [ -f "backend/app/main.py" ]; then
    cp backend/app/main.py backend/app/main.py.bak
    log_info "Backed up main.py"
fi

# Create new main.py
cat > backend/app/main.py << 'MAINEOF'
"""
NEMESIS Main Application - FastAPI Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("Starting NEMESIS services...")
    
    # Initialize services
    try:
        from backend.evidence import EvidenceRegistry
        EvidenceRegistry()
        print("  - Evidence registry initialized")
    except Exception as e:
        print(f"  - Evidence registry error: {e}")
    
    try:
        from backend.core.events import EventBus
        EventBus()
        print("  - Event bus initialized")
    except Exception as e:
        print(f"  - Event bus error: {e}")
    
    try:
        from backend.websocket import ConnectionManager
        ConnectionManager()
        print("  - WebSocket manager initialized")
    except Exception as e:
        print(f"  - WebSocket error: {e}")
    
    print("NEMESIS ready")
    yield
    
    # Shutdown
    print("Shutting down NEMESIS services...")


# Create FastAPI application
app = FastAPI(
    title="NEMESIS Intelligence Platform",
    description="Advanced threat detection and intelligence platform",
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

# Include routers
app.include_router(v1_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NEMESIS Intelligence Platform",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "api": "/api/v1",
            "health": "/health",
            "metrics": "/metrics"
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
MAINEOF

log_success "Created new main.py"

# Update runtime startup if exists
mkdir -p backend/runtime

cat > backend/runtime/startup.py << 'STARTUPEOF'
"""
Startup Handler - Initialize services on application start
"""

import logging

logger = logging.getLogger(__name__)


async def startup_handler():
    """Initialize all services"""
    logger.info("Starting NEMESIS services...")
    
    try:
        from backend.evidence import EvidenceRegistry
        registry = EvidenceRegistry()
        logger.info("Evidence registry initialized")
    except Exception as e:
        logger.error(f"Evidence registry failed: {e}")
    
    try:
        from backend.core.events import EventBus
        event_bus = EventBus()
        logger.info("Event bus initialized")
    except Exception as e:
        logger.error(f"Event bus failed: {e}")
    
    try:
        from backend.websocket import ConnectionManager
        ws_manager = ConnectionManager()
        logger.info("WebSocket manager initialized")
    except Exception as e:
        logger.error(f"WebSocket failed: {e}")
    
    logger.info("All services started")
    return True
STARTUPEOF

log_success "Created startup.py"

cat > backend/runtime/shutdown.py << 'SHUTDOWNEOF'
"""
Shutdown Handler - Clean up services on application shutdown
"""

import logging

logger = logging.getLogger(__name__)


async def shutdown_handler():
    """Clean up services"""
    logger.info("Shutting down NEMESIS services...")
    
    try:
        from backend.websocket import ConnectionManager
        ws_manager = ConnectionManager()
        await ws_manager.broadcast({
            "type": "shutdown",
            "message": "Server is shutting down"
        })
        logger.info("WebSocket shutdown complete")
    except Exception as e:
        logger.error(f"WebSocket shutdown error: {e}")
    
    logger.info("Services stopped")
    return True
SHUTDOWNEOF

log_success "Created shutdown.py"

log_success "Main application updated"
echo ""

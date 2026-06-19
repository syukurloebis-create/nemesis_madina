#!/bin/bash
# ============================================================================
# NEMESIS FASE 2 - Update Main Application
# Mengupdate main.py untuk menggunakan struktur baru
# ============================================================================

source "$(dirname "$0")/config.sh"

cd "$PROJECT_ROOT"

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║              FASE 2 - UPDATE MAIN APPLICATION                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Backup existing main.py
if [ -f "backend/app/main.py" ]; then
    cp backend/app/main.py backend/app/main.py.bak
    log_info "Backed up main.py"
fi

# Create new main.py
cat > backend/app/main.py << 'EOF'
"""
NEMESIS Main Application - FastAPI Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api import v1_router
from backend.api.middleware import setup_middleware
from backend.runtime.startup import startup_handler
from backend.runtime.shutdown import shutdown_handler
from backend.websocket.routes import router as ws_router
from backend.telemetry.metrics import setup_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await startup_handler()
    yield
    # Shutdown
    await shutdown_handler()


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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup custom middleware
setup_middleware(app)

# Setup metrics
setup_metrics(app)

# Include routers
app.include_router(v1_router)
app.include_router(ws_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "NEMESIS Intelligence Platform",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "api": "/api/v1",
            "websocket": "/ws",
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
EOF

log_success "Created new main.py"

# Update runtime startup if exists
if [ -f "backend/runtime/startup.py" ]; then
    cat > backend/runtime/startup.py << 'EOF'
"""
Startup Handler - Initialize services on application start
"""

import logging

logger = logging.getLogger(__name__)


async def startup_handler():
    """Initialize all services"""
    logger.info("Starting NEMESIS services...")
    
    # Initialize evidence registry
    from backend.evidence import EvidenceRegistry
    registry = EvidenceRegistry()
    logger.info("Evidence registry initialized")
    
    # Initialize event bus
    from backend.core.events import EventBus
    event_bus = EventBus()
    logger.info("Event bus initialized")
    
    # Initialize WebSocket manager
    from backend.websocket import ConnectionManager
    ws_manager = ConnectionManager()
    logger.info("WebSocket manager initialized")
    
    # Initialize graph
    from backend.graph import RelationshipGraph
    graph = RelationshipGraph()
    logger.info("Graph initialized")
    
    logger.info("All services started successfully")
    return True
EOF
    log_success "Updated startup.py"
fi

# Update runtime shutdown
if [ -f "backend/runtime/shutdown.py" ]; then
    cat > backend/runtime/shutdown.py << 'EOF'
"""
Shutdown Handler - Clean up services on application shutdown
"""

import logging

logger = logging.getLogger(__name__)


async def shutdown_handler():
    """Clean up services"""
    logger.info("Shutting down NEMESIS services...")
    
    # Close WebSocket connections
    from backend.websocket import ConnectionManager
    ws_manager = ConnectionManager()
    # Broadcast shutdown message
    await ws_manager.broadcast({
        "type": "shutdown",
        "message": "Server is shutting down"
    })
    logger.info("WebSocket connections closed")
    
    # Save state if needed
    logger.info("Services stopped successfully")
    return True
EOF
    log_success "Updated shutdown.py"
fi

log_success "Main application updated"
echo ""
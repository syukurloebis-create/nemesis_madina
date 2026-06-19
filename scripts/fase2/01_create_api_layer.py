#!/usr/bin/env python3
"""
NEMESIS FASE 2 - Create API Layer
Membuat struktur API yang terorganisir dengan versioning
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

API_DIR = PROJECT_ROOT / "backend" / "api"
V1_DIR = API_DIR / "v1"

def create_api_structure():
    """Buat struktur direktori API"""
    print("\n[DIR] Creating API directory structure...")
    
    API_DIR.mkdir(parents=True, exist_ok=True)
    V1_DIR.mkdir(parents=True, exist_ok=True)
    
    return True

def create_dependencies():
    """Buat dependencies.py - dependency injection"""
    content = '''"""
API Dependencies - Dependency Injection for FastAPI
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.evidence import EvidenceRegistry
from backend.websocket import ConnectionManager
from backend.core.events import EventBus
from backend.graph import RelationshipGraph


# Singleton instances
_evidence_registry = None
_connection_manager = None
_event_bus = None
_graph = None


def get_evidence_registry() -> EvidenceRegistry:
    """Get evidence registry singleton"""
    global _evidence_registry
    if _evidence_registry is None:
        _evidence_registry = EvidenceRegistry()
    return _evidence_registry


def get_connection_manager() -> ConnectionManager:
    """Get WebSocket connection manager singleton"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def get_event_bus() -> EventBus:
    """Get event bus singleton"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def get_graph() -> RelationshipGraph:
    """Get relationship graph singleton"""
    global _graph
    if _graph is None:
        _graph = RelationshipGraph()
    return _graph


# Type annotations for FastAPI dependency injection
EvidenceRegistryDep = Annotated[EvidenceRegistry, Depends(get_evidence_registry)]
ConnectionManagerDep = Annotated[ConnectionManager, Depends(get_connection_manager)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
GraphDep = Annotated[RelationshipGraph, Depends(get_graph)]


# Security
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Get current user from token (simplified for now)"""
    if credentials:
        return credentials.credentials
    return "anonymous"


CurrentUserDep = Annotated[Optional[str], Depends(get_current_user)]
'''
    
    file_path = API_DIR / "dependencies.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_middleware():
    """Buat middleware.py - custom middleware"""
    content = '''"""
API Middleware - Custom middleware for logging, metrics, etc.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request and response details"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Log request
        print(f"-> {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response
        duration_ms = (time.perf_counter() - start_time) * 1000
        print(f"<- {response.status_code} ({duration_ms:.2f}ms)")
        
        response.headers["X-Response-Time-Ms"] = str(int(duration_ms))
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect request metrics"""
    
    def __init__(self, app, metrics_registry):
        super().__init__(app)
        self.metrics = metrics_registry
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        duration = time.perf_counter() - start_time
        # Record metrics (simplified)
        
        return response


def setup_middleware(app):
    """Setup all middleware"""
    app.add_middleware(LoggingMiddleware)
    # Add more middleware as needed
    return app
'''
    
    file_path = API_DIR / "middleware.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_init():
    """Buat __init__.py untuk API"""
    content = '''"""
NEMESIS API Layer - Versioned REST API
"""

from backend.api.v1 import router as v1_router

__all__ = ['v1_router']
'''
    
    file_path = API_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_evidence_endpoints():
    """Buat evidence.py endpoints"""
    content = '''"""
Evidence API Endpoints - Version 1
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any

from backend.api.dependencies import EvidenceRegistryDep, CurrentUserDep
from backend.evidence.dto import Evidence, EvidenceType


router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_evidence(
    payload: Dict[str, Any],
    source: str,
    evidence_type: EvidenceType = EvidenceType.GENERIC,
    registry: EvidenceRegistryDep = None,
    current_user: CurrentUserDep = None
):
    """Create new evidence"""
    evidence = registry.create(
        payload=payload,
        source=source,
        evidence_type=evidence_type
    )
    return {
        "id": evidence.id,
        "hash": evidence.hash,
        "created_at": evidence.created_at.isoformat(),
        "message": "Evidence created successfully"
    }


@router.get("/{evidence_id}", response_model=Dict[str, Any])
async def get_evidence(
    evidence_id: str,
    registry: EvidenceRegistryDep = None
):
    """Get evidence by ID"""
    evidence = registry.get(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence.to_dict()


@router.post("/{evidence_id}/verify", response_model=Dict[str, Any])
async def verify_evidence(
    evidence_id: str,
    registry: EvidenceRegistryDep = None
):
    """Verify evidence integrity"""
    is_valid = registry.verify(evidence_id)
    return {
        "evidence_id": evidence_id,
        "valid": is_valid,
        "message": "Evidence verified" if is_valid else "Evidence integrity check failed"
    }


@router.get("/", response_model=List[Dict[str, Any]])
async def list_evidence(
    registry: EvidenceRegistryDep = None,
    limit: int = 100,
    offset: int = 0
):
    """List all evidence"""
    all_evidence = registry.list_all()
    paginated = all_evidence[offset:offset + limit]
    return [e.to_dict() for e in paginated]


@router.post("/{evidence_id}/custody", response_model=Dict[str, Any])
async def add_custody_event(
    evidence_id: str,
    action: str,
    reason: str,
    registry: EvidenceRegistryDep = None,
    current_user: CurrentUserDep = None
):
    """Add custody event to evidence"""
    evidence = registry.add_custody_event(
        evidence_id=evidence_id,
        action=action,
        actor=current_user or "system",
        reason=reason
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return {
        "evidence_id": evidence_id,
        "version": evidence.version,
        "message": "Custody event added"
    }


@router.get("/{evidence_id}/custody", response_model=List[Dict[str, Any]])
async def get_custody_chain(
    evidence_id: str,
    registry: EvidenceRegistryDep = None
):
    """Get custody chain for evidence"""
    evidence = registry.get(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return [
        {
            "action": e.action,
            "actor": e.actor,
            "timestamp": e.timestamp.isoformat(),
            "reason": e.reason
        }
        for e in evidence.custody_chain
    ]
'''
    
    file_path = V1_DIR / "evidence.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_events_endpoints():
    """Buat events.py endpoints"""
    content = '''"""
Events API Endpoints - Version 1
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.api.dependencies import EventBusDep
from backend.core.events.bus import Event


router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", status_code=202)
async def publish_event(
    event_type: str,
    data: Any,
    source: str,
    background_tasks: BackgroundTasks,
    event_bus: EventBusDep = None
):
    """Publish event to event bus"""
    event = Event(
        id=str(uuid.uuid4()),
        type=event_type,
        data=data,
        source=source,
        timestamp=datetime.now()
    )
    
    background_tasks.add_task(event_bus.publish, event)
    
    return {
        "event_id": event.id,
        "status": "accepted",
        "message": "Event published"
    }


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_event_history(
    event_type: Optional[str] = None,
    limit: int = 100,
    event_bus: EventBusDep = None
):
    """Get event history"""
    history = event_bus.get_history(event_type, limit)
    return [
        {
            "id": e.id,
            "type": e.type,
            "source": e.source,
            "timestamp": e.timestamp.isoformat(),
            "data": e.data
        }
        for e in history
    ]


@router.get("/metrics", response_model=Dict[str, Any])
async def get_event_metrics(
    event_bus: EventBusDep = None
):
    """Get event bus metrics"""
    return event_bus.get_metrics()


@router.post("/replay", response_model=Dict[str, Any])
async def replay_events(
    from_timestamp: str,
    to_timestamp: str,
    event_bus: EventBusDep = None
):
    """Replay events in time range"""
    from_dt = datetime.fromisoformat(from_timestamp)
    to_dt = datetime.fromisoformat(to_timestamp)
    
    result = await event_bus.replay(from_dt, to_dt)
    return result
'''
    
    # Add missing import
    content = "import uuid\n" + content
    
    file_path = V1_DIR / "events.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_graph_endpoints():
    """Buat graph.py endpoints"""
    content = '''"""
Graph API Endpoints - Version 1
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional

from backend.api.dependencies import GraphDep


router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/nodes", response_model=Dict[str, Any])
async def add_node(
    node_id: str,
    label: str,
    properties: Dict[str, Any] = None,
    graph: GraphDep = None
):
    """Add node to graph"""
    node = graph.add_node(node_id, label, **(properties or {}))
    return {
        "id": node.id,
        "label": node.label,
        "message": "Node added"
    }


@router.post("/edges", response_model=Dict[str, Any])
async def add_edge(
    source: str,
    target: str,
    label: str,
    weight: float = 1.0,
    properties: Dict[str, Any] = None,
    graph: GraphDep = None
):
    """Add edge to graph"""
    edge = graph.add_edge(source, target, label, weight, **(properties or {}))
    if not edge:
        raise HTTPException(status_code=400, detail="Nodes not found")
    return {
        "source": source,
        "target": target,
        "label": label,
        "message": "Edge added"
    }


@router.get("/nodes/{node_id}/neighbors", response_model=List[Dict[str, Any]])
async def get_neighbors(
    node_id: str,
    direction: str = "both",
    graph: GraphDep = None
):
    """Get neighbors of a node"""
    neighbors = graph.get_neighbors(node_id, direction)
    return [
        {"node": n, "label": l, "weight": w}
        for n, l, w in neighbors
    ]


@router.get("/metrics", response_model=Dict[str, Any])
async def get_graph_metrics(
    graph: GraphDep = None
):
    """Get graph metrics"""
    return graph.get_metrics()


@router.get("/shortest-path", response_model=Dict[str, Any])
async def get_shortest_path(
    source: str,
    target: str,
    graph: GraphDep = None
):
    """Find shortest path between nodes"""
    path = graph.get_shortest_path(source, target)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    return {
        "source": source,
        "target": target,
        "path": path,
        "length": len(path) - 1
    }
'''
    
    file_path = V1_DIR / "graph.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_intelligence_endpoints():
    """Buat intelligence.py endpoints"""
    content = '''"""
Intelligence API Endpoints - Version 1
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional

from backend.api.dependencies import GraphDep
from backend.graph.collusion_detector import CollusionDetector


router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/collusion/score", response_model=Dict[str, Any])
async def get_collusion_score(
    graph: GraphDep = None
):
    """Compute collusion detection score"""
    detector = CollusionDetector(graph)
    result = detector.compute_collusion_score()
    return result


@router.get("/collusion/triangles", response_model=List[tuple])
async def get_collusion_triangles(
    graph: GraphDep = None
):
    """Detect triangles in graph"""
    detector = CollusionDetector(graph)
    triangles = detector.detect_triangles()
    return triangles[:50]  # Limit for response


@router.get("/collusion/hubs", response_model=List[Dict[str, Any]])
async def get_high_degree_nodes(
    threshold: int = 5,
    graph: GraphDep = None
):
    """Detect high-degree nodes (potential hubs)"""
    detector = CollusionDetector(graph)
    hubs = detector.detect_high_degree_nodes(threshold)
    return [
        {"node_id": node_id, "degree": degree}
        for node_id, degree in hubs
    ]


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_graph(
    graph: GraphDep = None
):
    """Run full graph analysis"""
    detector = CollusionDetector(graph)
    collusion = detector.compute_collusion_score()
    metrics = graph.get_metrics()
    
    return {
        "collusion": collusion,
        "graph_metrics": metrics,
        "analysis_timestamp": datetime.now().isoformat()
    }
'''
    
    content = "from datetime import datetime\n" + content
    
    file_path = V1_DIR / "intelligence.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_health_endpoints():
    """Buat health.py endpoints"""
    content = '''"""
Health API Endpoints - Version 1
"""

from fastapi import APIRouter, Response
from typing import Dict, Any
from datetime import datetime

from backend.api.dependencies import EvidenceRegistryDep, EventBusDep


router = APIRouter(tags=["health"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/ready", response_model=Dict[str, Any])
async def readiness_check(
    evidence_registry: EvidenceRegistryDep = None,
    event_bus: EventBusDep = None
):
    """Readiness probe - checks dependencies"""
    status = "ready"
    issues = []
    
    # Check evidence registry
    try:
        evidence_registry.list_all()
    except Exception as e:
        status = "not_ready"
        issues.append(f"Evidence registry: {e}")
    
    # Check event bus
    try:
        event_bus.get_metrics()
    except Exception as e:
        status = "not_ready"
        issues.append(f"Event bus: {e}")
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "issues": issues
    }


@router.get("/health/live", response_model=Dict[str, Any])
async def liveness_check():
    """Liveness probe"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    evidence_registry: EvidenceRegistryDep = None,
    event_bus: EventBusDep = None,
    graph = None  # Would be GraphDep
):
    """Get system metrics"""
    return {
        "evidence": {
            "total": len(evidence_registry.list_all())
        },
        "events": event_bus.get_metrics(),
        "timestamp": datetime.now().isoformat()
    }
'''
    
    file_path = V1_DIR / "health.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_router_init():
    """Buat __init__.py untuk v1 router"""
    content = '''"""
API Version 1 - Router
"""

from fastapi import APIRouter

from backend.api.v1.evidence import router as evidence_router
from backend.api.v1.events import router as events_router
from backend.api.v1.graph import router as graph_router
from backend.api.v1.intelligence import router as intelligence_router
from backend.api.v1.health import router as health_router


router = APIRouter(prefix="/api/v1")

router.include_router(evidence_router)
router.include_router(events_router)
router.include_router(graph_router)
router.include_router(intelligence_router)
router.include_router(health_router)


__all__ = ['router']
'''
    
    file_path = V1_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 2: CREATE API LAYER")
    print("="*60)
    
    success = True
    success &= create_api_structure()
    success &= create_dependencies()
    success &= create_middleware()
    success &= create_init()
    success &= create_evidence_endpoints()
    success &= create_events_endpoints()
    success &= create_graph_endpoints()
    success &= create_intelligence_endpoints()
    success &= create_health_endpoints()
    success &= create_router_init()
    
    print("\n" + "="*60)
    if success:
        print("[OK] API LAYER CREATED")
        print(f"   Location: {API_DIR}")
        print("   Endpoints available:")
        print("     - POST   /api/v1/evidence")
        print("     - GET    /api/v1/evidence/{id}")
        print("     - POST   /api/v1/events")
        print("     - GET    /api/v1/events/history")
        print("     - POST   /api/v1/graph/nodes")
        print("     - POST   /api/v1/graph/edges")
        print("     - GET    /api/v1/intelligence/collusion/score")
        print("     - GET    /api/v1/health")
    else:
        print("[ERR] API LAYER CREATION FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    import uuid
    from datetime import datetime
    sys.exit(main())
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
import asyncio
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from infrastructure.database import init_db, close_db
from metrics import router as metrics_router
from trust_metrics import router as trust_metrics_router
from replay_metrics import router as replay_metrics_router
from risk_metrics import router as risk_metrics_router
from alert_engine import router as alert_router
from cases.api import router as cases_router
from security import auth_routes
from routers.snapshot import router as snapshot_router
from routers.integrity import router as integrity_router
from routers.historical import router as historical_router
from routers.reports import router as reports_router
from routers.upload_processor import router as upload_processor_router
from routers.vendors import router as vendors_router
from routers.governance import router as governance_router
from routers.evidence import router as evidence_router
from routers.graph import router as graph_router
from routers.finding import router as finding_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_connections: dict[str, list[str]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, client_id: str, websocket: WebSocket, user_id: str = None):
        async with self._lock:
            self.active_connections[client_id] = websocket
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = []
                self.user_connections[user_id].append(client_id)
        logger.info(f"✅ WebSocket connected: {client_id}")
    
    async def disconnect(self, client_id: str):
        async with self._lock:
            self.active_connections.pop(client_id, None)
            for user_id, clients in self.user_connections.items():
                if client_id in clients:
                    clients.remove(client_id)
                    break
        logger.info(f"❌ WebSocket disconnected: {client_id}")
    
    async def send_personal(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception:
                await self.disconnect(client_id)
    
    async def broadcast(self, message: dict, exclude_client: str = None):
        for client_id, ws in self.active_connections.items():
            if client_id == exclude_client:
                continue
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Nemesis Madina V8...")
    await init_db()
    logger.info("✅ Database ready")
    yield
    await close_db()
    logger.info("👋 Shutdown complete")


app = FastAPI(
    title="Nemesis Madina V8",
    version="8.0.0",
    description="Platform Audit & Inspeksi untuk Aparat Penegak Hukum",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        auth_message = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
        auth_data = json.loads(auth_message)
        if auth_data.get("type") != "auth":
            await websocket.close(code=1008, reason="Auth required")
            return
        token = auth_data.get("token")
        from security.auth import decode_token
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=1008, reason="Invalid token")
            return
        user_id = payload.get("sub") or client_id
        await manager.connect(client_id, websocket, user_id)
        while True:
            await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
    except:
        await manager.disconnect(client_id)


# ROUTERS - Hanya yang sudah terimport
app.include_router(cases_router)
app.include_router(auth_routes.router)
app.include_router(snapshot_router)
app.include_router(integrity_router)
app.include_router(historical_router)
app.include_router(reports_router)
app.include_router(upload_processor_router)
app.include_router(vendors_router)
app.include_router(governance_router)
app.include_router(evidence_router)
app.include_router(graph_router)
app.include_router(finding_router)
app.include_router(metrics_router)
app.include_router(trust_metrics_router)
app.include_router(replay_metrics_router)
app.include_router(risk_metrics_router)
app.include_router(alert_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nemesis-madina", "version": "8.0.0"}

@app.get("/")
async def root():
    return {"service": "Nemesis Madina V8", "status": "running"}

@app.get("/api/dashboard/summary")
async def dashboard_summary():
    from infrastructure.database import AsyncSessionLocal
    from sqlalchemy import select, func
    from cases.models import Case
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(Case))
        total_cases = result.scalar() or 0
    return {"total_cases": total_cases, "status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

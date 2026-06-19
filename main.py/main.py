from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.infrastructure.database import init_db, close_db
from backend.cases.api_direct import router as cases_router
from backend.metrics import router as metrics_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Nemesis Madina...")
    await init_db()
    logger.info("✅ Database ready")
    yield
    await close_db()
    logger.info("👋 Shutdown complete")


app = FastAPI(title="Nemesis Madina", version="8.0.0", lifespan=lifespan)

# CORS Middleware - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(cases_router)
app.include_router(metrics_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nemesis-madina"}

@app.get("/")
async def root():
    return {"service": "Nemesis Madina", "status": "running", "version": "8.0.0"}

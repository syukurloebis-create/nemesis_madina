# setup_api.ps1
# Script untuk mengkonfigurasi API Nemesis Madina dengan endpoint langsung ke database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEMESIS MADINA V8+ API SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Content for api_direct.py
$apiDirectContent = @'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
from datetime import datetime

from backend.infrastructure.database import get_db

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("/")
async def create_case(
    title: str,
    description: str = None,
    priority: str = "MEDIUM",
    db: AsyncSession = Depends(get_db)
):
    """Create a new case - direct SQL version"""
    case_id = str(uuid.uuid4())
    
    await db.execute(
        text("""
            INSERT INTO cases (id, title, description, status, priority, case_metadata, created_at)
            VALUES (:id, :title, :desc, 'DRAFT', :priority, '{}'::json, NOW())
        """),
        {"id": case_id, "title": title, "desc": description, "priority": priority.upper()}
    )
    await db.commit()
    
    return {
        "id": case_id,
        "title": title,
        "description": description,
        "status": "DRAFT",
        "priority": priority.upper(),
        "message": "Case created successfully"
    }


@router.get("/")
async def list_cases(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all cases - direct SQL version"""
    result = await db.execute(
        text("""
            SELECT id, title, description, status, priority, created_at
            FROM cases 
            WHERE status != 'DELETED'
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :skip
        """),
        {"limit": limit, "skip": skip}
    )
    rows = result.fetchall()
    return [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        }
        for row in rows
    ]


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Get case by ID - direct SQL version"""
    result = await db.execute(
        text("SELECT id, title, description, status, priority, created_at FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "status": row[3],
        "priority": row[4],
        "created_at": row[5].isoformat() if row[5] else None
    }


@router.delete("/{case_id}")
async def delete_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Soft delete a case"""
    await db.execute(
        text("UPDATE cases SET status = 'DELETED', updated_at = NOW() WHERE id = :id"),
        {"id": case_id}
    )
    await db.commit()
    return {"message": "Case deleted successfully", "case_id": case_id}


@router.get("/stats/total")
async def get_total_cases(db: AsyncSession = Depends(get_db)):
    """Get total cases count"""
    result = await db.execute(text("SELECT COUNT(*) FROM cases WHERE status != 'DELETED'"))
    count = result.scalar()
    return {"total_cases": count}
'@

# Content for main.py
$mainContent = @'
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from backend.infrastructure.database import init_db, close_db
from backend.cases import api_direct as cases_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("?? Starting Nemesis Madina V8+...")
    await init_db()
    logger.info("? Database ready")
    logger.info("?? API endpoints available at /cases")
    yield
    await close_db()
    logger.info("?? Shutdown complete")


app = FastAPI(
    title="Nemesis Madina V8+",
    version="8.0.0",
    description="Platform Audit & Inspeksi untuk Aparat Penegak Hukum",
    lifespan=lifespan
)

# Register routers
app.include_router(cases_api.router)

# Health check endpoints
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nemesis-madina", "version": "8.0.0"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/live")
async def live():
    return {"status": "alive"}

@app.get("/")
async def root():
    return {
        "service": "Nemesis Madina V8+",
        "version": "8.0.0",
        "description": "Platform Audit & Inspeksi untuk Aparat Penegak Hukum",
        "endpoints": {
            "health": "/health",
            "cases": "/cases",
            "cases_stats": "/cases/stats/total",
            "metrics": "/metrics"
        }
    }
'@

Write-Host "Step 1: Writing api_direct.py to containers..." -ForegroundColor Yellow

# Write to api1 container
Write-Host "  ? Writing to api1..." -ForegroundColor Green
$apiDirectContent | docker exec -i nemesis_madina-api1-1 sh -c "cat > /app/backend/cases/api_direct.py"

# Write to api2 container
Write-Host "  ? Writing to api2..." -ForegroundColor Green
$apiDirectContent | docker exec -i nemesis_madina-api2-1 sh -c "cat > /app/backend/cases/api_direct.py"

# Write to api3 container
Write-Host "  ? Writing to api3..." -ForegroundColor Green
$apiDirectContent | docker exec -i nemesis_madina-api3-1 sh -c "cat > /app/backend/cases/api_direct.py"

Write-Host ""
Write-Host "Step 2: Writing main.py to containers..." -ForegroundColor Yellow

# Write to api1 container
Write-Host "  ? Writing to api1..." -ForegroundColor Green
$mainContent | docker exec -i nemesis_madina-api1-1 sh -c "cat > /app/backend/main.py"

# Write to api2 container
Write-Host "  ? Writing to api2..." -ForegroundColor Green
$mainContent | docker exec -i nemesis_madina-api2-1 sh -c "cat > /app/backend/main.py"

# Write to api3 container
Write-Host "  ? Writing to api3..." -ForegroundColor Green
$mainContent | docker exec -i nemesis_madina-api3-1 sh -c "cat > /app/backend/main.py"

Write-Host ""
Write-Host "Step 3: Removing problematic middleware..." -ForegroundColor Yellow

# Remove middleware folders
docker exec nemesis_madina-api1-1 rm -rf /app/backend/middleware 2>$null
docker exec nemesis_madina-api2-1 rm -rf /app/backend/middleware 2>$null
docker exec nemesis_madina-api3-1 rm -rf /app/backend/middleware 2>$null

Write-Host "  ? Middleware removed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 4: Restarting API containers..." -ForegroundColor Yellow

# Restart API
docker-compose -f docker-compose.lb.yml restart api1 api2 api3

Write-Host ""
Write-Host "Waiting 15 seconds for services to stabilize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTING API ENDPOINTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test health
Write-Host "Test 1: Health Check" -ForegroundColor Yellow
$health = curl -s http://localhost/health
Write-Host $health -ForegroundColor Green
Write-Host ""

# Test create case
Write-Host "Test 2: Create Case (POST)" -ForegroundColor Yellow
$createResult = curl -s -X POST "http://localhost/cases?title=Nemesis%20Test%20Case&description=Testing%20PowerShell%20Setup&priority=HIGH"
Write-Host $createResult -ForegroundColor Green
Write-Host ""

# Test list cases
Write-Host "Test 3: List Cases (GET)" -ForegroundColor Yellow
$listResult = curl -s http://localhost/cases
Write-Host $listResult -ForegroundColor Green
Write-Host ""

# Test root endpoint
Write-Host "Test 4: Root Endpoint" -ForegroundColor Yellow
$rootResult = curl -s http://localhost/
Write-Host $rootResult -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "?? Dashboard URLs:" -ForegroundColor Yellow
Write-Host "  Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host ""
Write-Host "?? API Endpoints:" -ForegroundColor Yellow
Write-Host "  Health: http://localhost/health" -ForegroundColor Cyan
Write-Host "  Cases: http://localhost/cases" -ForegroundColor Cyan
Write-Host "  Create Case: POST http://localhost/cases?title=...&description=...&priority=..." -ForegroundColor Cyan
Write-Host ""
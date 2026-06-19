# run_backend.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STARTING NEMESIS MADINA BACKEND" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

cd C:\Users\LENOVO\nemesis_madina

# Set environment variables
$env:DATABASE_URL = "postgresql+asyncpg://nemesis:nemesis123@localhost:5432/nemesis_db"
$env:SECRET_KEY = "nemesis-super-secret-key-change-in-production"
$env:ENVIRONMENT = "development"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:NATS_URL = "nats://localhost:4222"

# Start PostgreSQL if not running
$pgRunning = docker ps --filter "name=postgres" --format "{{.Status}}" | Select-String "Up"
if (-not $pgRunning) {
    Write-Host "Starting PostgreSQL..." -ForegroundColor Yellow
    docker start nemesis_madina-postgres-1
    Start-Sleep -Seconds 5
}

Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

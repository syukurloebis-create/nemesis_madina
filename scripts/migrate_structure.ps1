# migrate_structure.ps1
# Migrate to new structure

Write-Host "Migrating to new structure..." -ForegroundColor Cyan

$ProjectRoot = "C:\Users\LENOVO\nemesis_madina"
Set-Location $ProjectRoot

# Create new structure
Write-Host "Creating new directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "deployment/docker" -Force | Out-Null
New-Item -ItemType Directory -Path "deployment/compose" -Force | Out-Null
New-Item -ItemType Directory -Path "deployment/k8s" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/prometheus" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/grafana/provisioning" -Force | Out-Null
New-Item -ItemType Directory -Path "monitoring/grafana/dashboards" -Force | Out-Null
New-Item -ItemType Directory -Path "storage/backups" -Force | Out-Null
New-Item -ItemType Directory -Path "storage/snapshots" -Force | Out-Null
New-Item -ItemType Directory -Path "storage/reports" -Force | Out-Null
New-Item -ItemType Directory -Path "storage/logs" -Force | Out-Null
New-Item -ItemType Directory -Path "docs/api" -Force | Out-Null
New-Item -ItemType Directory -Path "docs/architecture" -Force | Out-Null
New-Item -ItemType Directory -Path "scripts" -Force | Out-Null

# Move Docker files
Write-Host "Moving Docker configurations..." -ForegroundColor Yellow
if (Test-Path "Dockerfile") { Move-Item "Dockerfile" "deployment/docker/Dockerfile" -Force }
if (Test-Path "Dockerfile.prod") { Move-Item "Dockerfile.prod" "deployment/docker/Dockerfile.prod" -Force }
if (Test-Path ".dockerignore") { Move-Item ".dockerignore" "deployment/docker/.dockerignore" -Force }

# Move Compose files
Write-Host "Moving Compose configurations..." -ForegroundColor Yellow
if (Test-Path "docker-compose.lb.yml") { Copy-Item "docker-compose.lb.yml" "deployment/compose/docker-compose.yml" -Force }
if (Test-Path "docker-compose.prod.yml") { Move-Item "docker-compose.prod.yml" "deployment/compose/docker-compose.prod.yml" -Force }
if (Test-Path "docker-compose.observability.yml") { Move-Item "docker-compose.observability.yml" "deployment/compose/docker-compose.monitoring.yml" -Force }

# Move Monitoring configs
Write-Host "Moving monitoring configurations..." -ForegroundColor Yellow
if (Test-Path "prometheus") { Move-Item "prometheus/*" "monitoring/prometheus/" -Force }
if (Test-Path "grafana") { Move-Item "grafana/*" "monitoring/grafana/" -Force }

# Move K8s manifests
Write-Host "Moving Kubernetes manifests..." -ForegroundColor Yellow
if (Test-Path "k8s") { Move-Item "k8s/*" "deployment/k8s/" -Force }

# Move scripts
Write-Host "Moving scripts..." -ForegroundColor Yellow
if (Test-Path "scripts/*.py") { Move-Item "scripts/*.py" "backend/scripts/" -Force }
Copy-Item "cleanup.ps1" "scripts/cleanup.ps1" -Force

# Create symbolic links for compatibility (optional)
Write-Host "Creating compatibility symlinks..." -ForegroundColor Yellow
New-Item -ItemType SymbolicLink -Path "docker-compose.yml" -Target "deployment/compose/docker-compose.yml" -Force

Write-Host ""
Write-Host "Migration complete!" -ForegroundColor Green
Write-Host "Run cleanup.ps1 next to remove duplicate files" -ForegroundColor Yellow
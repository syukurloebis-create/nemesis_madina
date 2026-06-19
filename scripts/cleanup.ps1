# cleanup.ps1 - Simple version
# Nemesis Madina Cleanup Script

param(
    [switch]$DryRun = $false,
    [switch]$RemoveBackups = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEMESIS MADINA CLEANUP SCRIPT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dry Run Mode: $DryRun" -ForegroundColor Yellow
Write-Host "Remove Backups: $RemoveBackups" -ForegroundColor Yellow
Write-Host ""

$ProjectRoot = "C:\Users\LENOVO\nemesis_madina"
Set-Location $ProjectRoot

$deletedCount = 0
$movedCount = 0

function Remove-File {
    param($Path, $Desc)
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $Desc" -ForegroundColor Yellow
        } else {
            Remove-Item $Path -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Deleted: $Desc" -ForegroundColor Green
            $script:deletedCount++
        }
    }
}

function Remove-Folder {
    param($Path, $Desc)
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete folder: $Desc" -ForegroundColor Yellow
        } else {
            Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Deleted folder: $Desc" -ForegroundColor Green
            $script:deletedCount++
        }
    }
}

function Move-Folder {
    param($Source, $Dest, $Desc)
    if (Test-Path $Source) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would move: $Desc" -ForegroundColor Yellow
        } else {
            $destPath = Split-Path $Dest -Parent
            if (-not (Test-Path $destPath)) {
                New-Item -ItemType Directory -Path $destPath -Force | Out-Null
            }
            Move-Item $Source $Dest -Force -ErrorAction SilentlyContinue
            Write-Host "  ✓ Moved: $Desc" -ForegroundColor Green
            $script:movedCount++
        }
    }
}

# ============================================
# HAPUS FILE DUPLIKAT DI ROOT
# ============================================
Write-Host ""
Write-Host "STEP 1: Removing duplicate files in root..." -ForegroundColor Magenta

$duplicateFiles = @(
    "api_backup.py", "api_backup_*.py", "api_fix.py", "api_fixed.py",
    "api_new.py", "api_patched.py", "api_to_fix.py", "api_updated.py",
    "api_with_endpoints.py", "api_current.py",
    "__init__backup.py", "__init__clean.py", "__init__correct.py", "__init__final.py",
    "main_api1.py", "main_backup.py", "main_no_middleware.py", "main_simple.py",
    "test_*.py", "*.pyc"
)

foreach ($pattern in $duplicateFiles) {
    Get-ChildItem -Path $ProjectRoot -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-File -Path $_.FullName -Desc $_.Name
    }
}

# ============================================
# HAPUS CACHE
# ============================================
Write-Host ""
Write-Host "STEP 2: Removing cache files..." -ForegroundColor Magenta

Get-ChildItem -Path $ProjectRoot -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Folder -Path $_.FullName -Desc $_.FullName
}

Remove-Folder -Path ".pytest_cache" -Desc "Pytest cache"
Remove-Folder -Path ".mypy_cache" -Desc "Mypy cache"
Remove-Folder -Path ".ruff_cache" -Desc "Ruff cache"
Remove-Folder -Path "htmlcov" -Desc "HTML coverage"

# ============================================
# ORGANISIR STORAGE
# ============================================
Write-Host ""
Write-Host "STEP 3: Organizing storage folders..." -ForegroundColor Magenta

# Create storage folders
if (-not $DryRun) {
    New-Item -ItemType Directory -Path "storage/backups" -Force | Out-Null
    New-Item -ItemType Directory -Path "storage/snapshots" -Force | Out-Null
    New-Item -ItemType Directory -Path "storage/reports" -Force | Out-Null
    New-Item -ItemType Directory -Path "storage/logs" -Force | Out-Null
    Write-Host "  ✓ Created storage directories" -ForegroundColor Green
}

Move-Folder -Source "reports" -Dest "storage/reports" -Desc "Reports"
Move-Folder -Source "snapshots" -Dest "storage/snapshots" -Desc "Snapshots"

if (Test-Path "fase0_logs") {
    Move-Folder -Source "fase0_logs" -Dest "storage/logs/fase0" -Desc "Fase0 logs"
}

if (Test-Path "logs") {
    Move-Folder -Source "logs" -Dest "storage/logs" -Desc "Logs"
}

# ============================================
# HAPUS TEMP FILES
# ============================================
Write-Host ""
Write-Host "STEP 4: Removing temporary files..." -ForegroundColor Magenta

$tempFiles = @("*.log", "*.tmp", "*.temp", "*.bak", "response.json", "sample_data.json", "openapi.json")
foreach ($pattern in $tempFiles) {
    Get-ChildItem -Path $ProjectRoot -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-File -Path $_.FullName -Desc $_.Name
    }
}

# ============================================
# HAPUS BACKUP (OPSIONAL)
# ============================================
if ($RemoveBackups) {
    Write-Host ""
    Write-Host "STEP 5: Removing backup folders..." -ForegroundColor Magenta
    Remove-Folder -Path "backend.backup.20260604" -Desc "Backup folder 1"
    Remove-Folder -Path "backend.backup.20260604_213135" -Desc "Backup folder 2"
    Remove-Folder -Path "backup_hash" -Desc "Hash backup"
    Remove-Folder -Path "archive" -Desc "Archive"
    Remove-Folder -Path "backups" -Desc "Old backups"
} else {
    Write-Host ""
    Write-Host "STEP 5: Skipping backup removal (use -RemoveBackups flag)" -ForegroundColor Gray
}

# ============================================
# SUMMARY
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "  DRY RUN COMPLETE - No changes made" -ForegroundColor Yellow
} else {
    Write-Host "  CLEANUP COMPLETE" -ForegroundColor Green
    Write-Host "  Items deleted: $deletedCount" -ForegroundColor Green
    Write-Host "  Items moved: $movedCount" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Magenta
Write-Host "1. Run: docker-compose -f docker-compose.lb.yml down && docker-compose -f docker-compose.lb.yml up -d" -ForegroundColor White
Write-Host "2. Test: curl http://localhost/health" -ForegroundColor White
Write-Host ""
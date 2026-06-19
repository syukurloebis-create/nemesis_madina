#!/usr/bin/env python3
"""
NEMESIS FASE 8 - Create Management Scripts
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def create_start_script():
    """Create start_server.sh"""
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Start Server Script
# ============================================================================

cd "$(dirname "$0")/.."

export PYTHONPATH="$PWD"

echo "Starting NEMESIS server..."
echo ""

# Check if already running
if pgrep -f "uvicorn backend.app.main:app" > /dev/null; then
    echo "Server is already running"
    exit 1
fi

# Start server
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "To stop: ./scripts/stop_server.sh"
'''
    
    file_path = PROJECT_ROOT / "scripts" / "start_server.sh"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    file_path.chmod(0o755)
    print(f"  [OK] Created: {file_path}")
    return True


def create_stop_script():
    """Create stop_server.sh"""
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Stop Server Script
# ============================================================================

cd "$(dirname "$0")/.."

echo "Stopping NEMESIS server..."

# Kill uvicorn processes
pkill -f "uvicorn backend.app.main:app" 2>/dev/null

# Wait for processes to terminate
sleep 2

# Verify stopped
if pgrep -f "uvicorn backend.app.main:app" > /dev/null; then
    echo "Force killing remaining processes..."
    pkill -9 -f "uvicorn backend.app.main:app" 2>/dev/null
fi

echo "Server stopped"
'''
    
    file_path = PROJECT_ROOT / "scripts" / "stop_server.sh"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    file_path.chmod(0o755)
    print(f"  [OK] Created: {file_path}")
    return True


def create_monitor_script():
    """Create monitor.sh - without Unicode"""
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Monitor Script
# ============================================================================

API_URL="http://localhost:8000"

echo "============================================================"
echo "NEMESIS MONITOR"
echo "============================================================"
echo ""

# Check server status
echo "[1] Server Status:"
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo "    [OK] Server is running"
else
    echo "    [FAIL] Server is not responding"
    exit 1
fi

# Health check
echo ""
echo "[2] Health Check:"
curl -s "$API_URL/health" | python -m json.tool 2>/dev/null

# Metrics
echo ""
echo "[3] Metrics:"
curl -s "$API_URL/metrics" | python -m json.tool 2>/dev/null

# System info
echo ""
echo "[4] System Info:"
echo "    Time: $(date)"
echo "    Uptime: $(uptime 2>/dev/null || echo "N/A")"

echo ""
echo "============================================================"
'''
    
    file_path = PROJECT_ROOT / "scripts" / "monitor.sh"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    file_path.chmod(0o755)
    print(f"  [OK] Created: {file_path}")
    return True


def create_backup_script():
    """Create backup_database.sh"""
    content = '''#!/bin/bash
# ============================================================================
# NEMESIS Database Backup Script
# ============================================================================

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/nemesis_db_$TIMESTAMP.sql"

echo "Backing up database to: $BACKUP_FILE"

# Check if pg_dump is available
if command -v pg_dump &> /dev/null; then
    pg_dump -h localhost -U nemesis -d nemesis_db -f "$BACKUP_FILE" 2>/dev/null
    if [ $? -eq 0 ]; then
        gzip "$BACKUP_FILE"
        echo "[OK] Backup completed: ${BACKUP_FILE}.gz"
    else
        echo "[FAIL] Backup failed"
        exit 1
    fi
else
    echo "[WARN] pg_dump not found - skipping database backup"
fi

# Clean old backups (keep last 7 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete 2>/dev/null

echo ""
echo "Backup location: $BACKUP_DIR"
'''
    
    file_path = PROJECT_ROOT / "scripts" / "backup_database.sh"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    file_path.chmod(0o755)
    print(f"  [OK] Created: {file_path}")
    return True


def main():
    print("\n" + "="*60)
    print("FASE 8: CREATE MANAGEMENT SCRIPTS")
    print("="*60)
    
    create_start_script()
    create_stop_script()
    create_monitor_script()
    create_backup_script()
    
    print("\n" + "="*60)
    print("[OK] Management scripts created")
    print("="*60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

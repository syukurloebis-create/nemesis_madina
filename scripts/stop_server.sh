#!/bin/bash
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

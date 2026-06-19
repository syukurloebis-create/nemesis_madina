#!/bin/bash
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

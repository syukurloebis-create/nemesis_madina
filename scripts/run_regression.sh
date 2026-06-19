#!/bin/bash
# Full regression test suite

echo "=========================================="
echo "FULL REGRESSION TEST"
echo "=========================================="
echo ""

# Unit tests
echo "[1/5] Running unit tests..."
python -m pytest tests/unit -v --tb=short 2>&1 | tail -30

# WebSocket broadcast test
echo ""
echo "[2/5] Running broadcast test..."
python scripts/broadcast_test.py 2>&1 | tail -20

# Ping test
echo ""
echo "[3/5] Running ping test..."
python scripts/ping_test.py 2>&1 | tail -15

# Soak test (60 seconds)
echo ""
echo "[4/5] Running soak test (60s)..."
timeout 120 python scripts/soak_test.py 2>&1 | tail -25

# Worker test (quick check)
echo ""
echo "[5/5] Testing worker (10s)..."
timeout 15 python worker_outbox.py 2>&1 | head -25

echo ""
echo "=========================================="
echo "REGRESSION TEST COMPLETE"
echo "=========================================="

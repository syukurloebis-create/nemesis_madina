#!/bin/bash
# Start NEMESIS with logging

LOG_FILE="logs/nemesis_$(date +%Y%m%d_%H%M%S).log"
mkdir -p logs

echo "Starting NEMESIS with logging to $LOG_FILE"
echo "PID: $$" >> $LOG_FILE

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload >> $LOG_FILE 2>&1 &
echo $! > .server.pid

echo "Server started. Monitor with: tail -f $LOG_FILE"

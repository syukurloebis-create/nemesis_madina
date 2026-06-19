#!/bin/bash
# Production start script for Linux

export APP_ENV=production
export LOG_LEVEL=INFO

# Start with 2 workers (adjust based on CPU cores)
uvicorn backend.app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    --access-log

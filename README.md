# NEMESIS Intelligence Platform

## Overview
Advanced threat detection and intelligence platform.

## Quick Start

### Run Locally
```bash
cd nemesis_madina
export PYTHONPATH=$PWD
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Run with Docker
```bash
docker build -t nemesis:latest -f Dockerfile.simple .
docker run -p 8000:8000 nemesis:latest
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

## Architecture
```
backend/
├── api/          # REST API endpoints
├── core/         # Business logic
├── evidence/     # Evidence management
├── intelligence/ # AI/ML capabilities
├── lineage/      # Data lineage
├── schema/       # Schema registry
├── telemetry/    # Observability
└── websocket/    # Real-time communication
```

## Testing
```bash
pytest tests/unit -v
```
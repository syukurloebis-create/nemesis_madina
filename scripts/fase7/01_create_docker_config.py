#!/usr/bin/env python3
"""
NEMESIS FASE 7 - Create Docker Configuration
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def create_dockerfile():
    """Create Dockerfile for production"""
    print("\n[1/6] Creating Dockerfile...")
    
    content = '''# NEMESIS Production Dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY alembic.ini .
COPY pytest.ini .
COPY .env.production .env

# Make sure scripts are executable
RUN chmod +x ./scripts/*.sh

# Create non-root user
RUN useradd -m -u 1000 nemesis && chown -R nemesis:nemesis /app
USER nemesis

# Environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    file_path = PROJECT_ROOT / "Dockerfile"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_docker_compose():
    """Create docker-compose.yml for local development"""
    print("\n[2/6] Creating docker-compose.yml...")
    
    content = '''# NEMESIS Docker Compose Configuration
version: '3.8'

services:
  # API Service
  api:
    build: .
    container_name: nemesis-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://nemesis:password@postgres:5432/nemesis
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
    depends_on:
      - postgres
      - redis
      - nats
    volumes:
      - ./backend:/app/backend
      - ./logs:/app/logs
    networks:
      - nemesis-network
    restart: unless-stopped

  # WebSocket Service
  websocket:
    build: .
    container_name: nemesis-websocket
    command: uvicorn backend.websocket.routes:app --host 0.0.0.0 --port 8001
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - nats
    networks:
      - nemesis-network
    restart: unless-stopped

  # Worker Service
  worker:
    build: .
    container_name: nemesis-worker
    command: python scripts/worker.py
    environment:
      - DATABASE_URL=postgresql://nemesis:password@postgres:5432/nemesis
      - REDIS_URL=redis://redis:6379
      - NATS_URL=nats://nats:4222
    depends_on:
      - postgres
      - redis
      - nats
    volumes:
      - ./logs:/app/logs
    networks:
      - nemesis-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: nemesis-postgres
    environment:
      - POSTGRES_USER=nemesis
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=nemesis
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - nemesis-network
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: nemesis-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - nemesis-network
    restart: unless-stopped

  # NATS Message Bus
  nats:
    image: nats:2.10-alpine
    container_name: nemesis-nats
    ports:
      - "4222:4222"
      - "8222:8222"
    command: -js
    networks:
      - nemesis-network
    restart: unless-stopped

  # Prometheus Metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: nemesis-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - nemesis-network
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: nemesis-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    networks:
      - nemesis-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  nemesis-network:
    driver: bridge
'''
    
    file_path = PROJECT_ROOT / "docker-compose.yml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_dockerignore():
    """Create .dockerignore file"""
    print("\n[3/6] Creating .dockerignore...")
    
    content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/

# Git
.git/
.gitignore

# Logs
*.log
logs/

# Environment
.env
.env.local

# Documentation
docs/
README.md

# Docker
Dockerfile
docker-compose*.yml

# Node
node_modules/
npm-debug.log

# OS
.DS_Store
Thumbs.db
'''
    
    file_path = PROJECT_ROOT / ".dockerignore"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_prometheus_config():
    """Create prometheus.yml configuration"""
    print("\n[4/6] Creating Prometheus configuration...")
    
    content = '''# Prometheus Configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'nemesis-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
  
  - job_name: 'nemesis-websocket'
    static_configs:
      - targets: ['websocket:8001']
    metrics_path: '/metrics'
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
  
  - job_name: 'nats'
    static_configs:
      - targets: ['nats:7777']
'''
    
    file_path = PROJECT_ROOT / "prometheus.yml"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_env_production():
    """Create .env.production file"""
    print("\n[5/6] Creating .env.production...")
    
    content = '''# NEMESIS Production Environment Variables

# Application
APP_NAME=NEMESIS
APP_ENV=production
APP_DEBUG=false
APP_VERSION=2.0.0

# Database
DATABASE_URL=postgresql://nemesis:${DB_PASSWORD}@postgres:5432/nemesis
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=3600

# NATS
NATS_URL=nats://nats:4222
NATS_STREAM_NAME=nemesis_events

# Security
SECRET_KEY=${SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Logging
LOG_LEVEL=INFO
LOG_JSON_FORMAT=true

# Metrics
METRICS_ENABLED=true
PROMETHEUS_PORT=8000

# WebSocket
WS_MAX_CONNECTIONS=1000
WS_PING_INTERVAL=20
WS_PING_TIMEOUT=10

# ML Model
ML_MODEL_PATH=/app/models
ML_BATCH_SIZE=100
'''
    
    file_path = PROJECT_ROOT / ".env.production"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_worker_script():
    """Create worker.py for background tasks"""
    print("\n[6/6] Creating worker script...")
    
    content = '''#!/usr/bin/env python3
"""
NEMESIS Background Worker
"""

import asyncio
import signal
import sys
from datetime import datetime

from backend.telemetry.logging import get_logger
from backend.telemetry.metrics import metrics_registry

logger = get_logger("worker")
running = True


def signal_handler():
    """Handle shutdown signals"""
    global running
    logger.info("Received shutdown signal")
    running = False


async def process_events():
    """Process events from queue"""
    from backend.core.events import EventBus
    bus = EventBus()
    
    # Subscribe to all events
    async def handler(event):
        logger.debug(f"Processing event: {event.type}")
        metrics_registry.counter("worker_events_processed", 1)
    
    bus.subscribe("*", handler)
    
    while running:
        await asyncio.sleep(1)
    
    logger.info("Worker stopped")


async def main():
    """Main worker loop"""
    logger.info("NEMESIS Worker starting...")
    
    # Set up signal handlers
    loop = asyncio.get_event_loop()
    for sig in [signal.SIGTERM, signal.SIGINT]:
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await process_events()
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    file_path = PROJECT_ROOT / "scripts" / "worker.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 7: CREATE DOCKER CONFIGURATION")
    print("="*60)
    
    create_dockerfile()
    create_docker_compose()
    create_dockerignore()
    create_prometheus_config()
    create_env_production()
    create_worker_script()
    
    print("\n" + "="*60)
    print("[OK] Docker configuration created")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
# NEMESIS Deployment Guide

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

## Quick Start

```bash
# Clone repository
git clone <repository>
cd nemesis_madina

# Copy environment file
cp .env.production .env

# Edit environment variables
vim .env

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost:8000/health
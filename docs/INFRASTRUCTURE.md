# NEMESIS — Infrastructure Reference

**Last Updated:** 2026-09-19
**Version:** CP2.5.1

## Health Endpoints

### /health — Basic
Returns static status. Always HTTP 200.

### /health/live — Liveness Probe
Returns liveness status. Always HTTP 200.

### /health/ready — Readiness Probe
Verifies actual dependencies:
- Database connectivity via check_db_health()
- Redis connectivity via redis.asyncio ping

**Response:**
- HTTP 200 if all checks pass
- HTTP 503 if any check fails

**Checks:**
- database: true | false
- redis: true | false | "skipped"

## Known Limitation: Redis Wiring

Status: Infrastructure-ready but NOT activated.

Current state:
- Redis container running (redis:7-alpine)
- Config schema exists (backend/config/cache.py)
- Custom client exists (backend/cache/redis_cache.py)
- MISSING: redis package in requirements.txt
- MISSING: ApplicationSettings.cache wiring
- MISSING: CACHE_TYPE=redis in docker-compose

Behavior:
- Cache defaults to MEMORY
- /health/ready reports redis: "skipped"
- Redis container idles

Activation Sprint (Deferred):
1. Add redis>=5.0.0 to requirements.txt
2. Wire self.cache in ApplicationSettings
3. Set CACHE_TYPE=redis + REDIS_HOST=redis
4. Rebuild API
5. Integration tests

## Container Stack

| Service | Image | Restart Policy |
|---------|-------|----------------|
| api | python:3.12-slim | unless-stopped |
| postgres | postgres:15 | unless-stopped |
| redis | redis:7-alpine | unless-stopped |
| nginx | nginx:alpine | unless-stopped |

## Docker Operations

Reload code (bind mount):
  docker compose up -d --force-recreate api

Restart (does NOT reload):
  docker compose restart api

## Baseline Contracts (FROZEN)

- Risk Engine v3: 47.58 MEDIUM
- Graph F3: 4177 entities / 2424 relationships
- Tag: f3-graph-intelligence-v1 -> 579e020

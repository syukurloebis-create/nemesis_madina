# NEMESIS V8+ - OpenAPI Endpoint Report

## Auth Endpoints
- POST /auth/login
- POST /auth/logout
- GET /auth/me
- POST /auth/register

## Cases Endpoints
- GET /cases
- POST /cases
- GET /cases/{case_id}
- PUT /cases/{case_id}
- DELETE /cases/{case_id}
- GET /cases/stats/total

## Replay/Event Sourcing
- GET /replay/case/{case_id}/timeline
- GET /replay/case/{case_id}/history
- GET /replay/case/{case_id}/state/version/{version}
- GET /replay/case/{case_id}/state/timestamp/{timestamp}
- POST /replay/case/{case_id}/replay

## Historical Reconstruction
- GET /historical/case/{case_id}/state
- GET /historical/case/{case_id}/timeline
- GET /historical/case/{case_id}/audit-trail
- GET /historical/case/{case_id}/workflow
- GET /historical/case/{case_id}/forensic-report
- GET /historical/case/{case_id}/compare-versions

## Snapshot Management
- GET /snapshots/case/{case_id}
- GET /snapshots/case/{case_id}/latest
- GET /snapshots/case/{case_id}/version/{version}
- POST /snapshots/case/{case_id}
- DELETE /snapshots/case/{case_id}/old

## Lineage & Integrity
- GET /lineage/case/{case_id}
- GET /lineage/case/{case_id}/verify
- POST /lineage/replay

## Health & Metrics
- GET /health
- GET /metrics
- GET /readiness
- GET /liveness


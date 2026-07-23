# Freeze Register — ADR-030 Revision v2

## Scope: Only truly dormant components are frozen.

### Type A — DORMANT (Blocked from Runtime)

| ID | Component | File | Status |
| :--- | :--- | :--- | :--- |
| FR-001 | GetDashboardQueryHandler | `backend/application/queries/get_dashboard_handler.py` | FROZEN |
| FR-002 | GetDashboardQuery | `backend/application/queries/dashboard_query.py` | FROZEN |
| FR-005 | WorkflowService | `backend/services/workflow_service.py` | FROZEN |

### Type B — ACTIVE DEVELOPMENT (Not Frozen)

| ID | Component | File | Status |
| :--- | :--- | :--- | :--- |
| FR-003 | DashboardReadRepository | `backend/infrastructure/repositories/dashboard_read_repository.py` | ACTIVE |
| FR-004 | DashboardProjection | `backend/infrastructure/projections/dashboard_projection.py` | ACTIVE |
| FR-007 | ProjectionCheckpoint | `backend/infrastructure/models/projection_checkpoint.py` | ACTIVE |

### Type C — PRESERVED ARCHITECTURAL RUNTIME

Components are frozen from redesign, but may remain reachable in production runtime.

**Allowed:**
- compatibility fixes
- security patches
- operational maintenance

**Blocked:**
- feature expansion
- architectural redesign
- responsibility migration

| ID | Component | File | Status |
| :--- | :--- | :--- | :--- |
| FR-008 | OutboxPublisher | `backend/infrastructure/outbox/publisher.py` | FROZEN |
| FR-009 | AnalyzeCaseCommandHandler | `backend/application/commands/analysis_mapper.py` | FROZEN |

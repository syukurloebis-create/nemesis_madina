# Legacy CQRS Architecture Audit

**Audit Date:** 2026-07-23

**Audit Scope:**
- Runtime dependency audit
- Bootstrap registration audit
- Router reference audit
- Integration test audit
- Worker/CLI reference audit

## Status
**Legacy Candidate** - Under Architecture Review

## Evidence Source

Audit performed from:
- `backend/bootstrap/container_builder.py`
- `backend/bootstrap/container.py`
- `backend/main.py`
- `backend/routers/*`
- `grep` runtime reference audit
- Integration test inventory
- Worker/CLI scan

## Audit Limitations

This audit covers:

- HTTP runtime
- Bootstrap container
- Router registrations
- Integration tests
- Audited worker/CLI directories

This audit does not prove absence of references in:
- External tooling
- Archived branches
- Plugins
- Future runtime integrations

## Components Under Review

### AnalyzeCaseCommandHandler

**Status**: Legacy Candidate

**Evidence**:
- ❌ Not registered in `ApplicationContainer`
- ❌ Not referenced by `backend/main.py`
- ❌ Not imported by routers
- ✅ Referenced by `tests/integration/test_command_flow.py`
- ⚠️ Constructor signature has diverged from runtime
- ⚠️ Dependency `fraud_engine` not found in current runtime

**Inference**:
Current HTTP application runtime does not instantiate this component.
Further dependency analysis is required before decommissioning.

---

### ProjectionRebuilder

**Status**: Under Review

**Evidence**:
- ❌ Not registered in `ApplicationContainer`
- ❌ Not called by router/main.py
- ❌ No references found in audited worker/CLI directories
- ⚠️ `EventStoreRepository` still exists (via alias)
- ⚠️ `DashboardProjection` still exists

**Inference**:
Dependency graph incomplete. Need to verify if used by maintenance tools.

---

### OutboxPublisher

**Status**: Under Review

**Evidence**:
- ❌ Not registered in `ApplicationContainer`
- ❌ Not called by router/main.py
- ❌ No references found in audited worker/CLI directories
- ⚠️ `IEventDispatcher` still has implementation (`InMemoryEventDispatcher`)
- ⚠️ `OutboxRepository` still exists

**Inference**:
Dependency graph incomplete. Need to verify if used by background services.

---

### EventStoreRepository

**Status**: Active (infrastructure component)

**Evidence**:
- ✅ Still exists via alias at `backend/infrastructure/event_store.py`
- ✅ Points to `backend/cases/event_store.py`

**Inference**:
Usage verification in progress.

---

### RiskApplicationService

**Status**: Active (HTTP application write-side)

**Evidence**:
- ✅ Registered in `ApplicationContainer`
- ✅ Called by routers
- ✅ Uses `RiskProjectionService` and `RiskCommandRepository`

**Inference**:
Keep. This is the current write-side architecture for HTTP requests.

---

## Current Write-Side Architecture (Active)

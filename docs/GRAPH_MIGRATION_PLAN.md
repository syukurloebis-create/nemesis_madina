# Graph Migration Plan - NEMESIS

## Executive Summary

Migrate from 4 fragmented graph runtimes to single DDD-based graph runtime.

## Current State
- 4 graph runtimes (DDD, Legacy, Intelligence, In-Memory)
- 2 GraphWriteRepository implementations
- 3 direct SQL INSERT paths
- case_id = NULL in graph_entities

## Target State
- Single GraphAggregate domain
- Single GraphPersistenceService
- Single GraphWriteRepository
- All writes via repository pattern
- All entities have case_id, business_key

## Migration Phases

### Phase 0: Architecture Freeze (1 day)
- [x] Create GRAPH_ARCHITECTURE_DECISION.md
- [x] Create GRAPH_DEPENDENCY_MAP.md
- [x] Create GRAPH_MIGRATION_PLAN.md
- [x] Create GRAPH_DEPRECATION_PLAN.md
- [ ] Architecture review and approval

### Phase 1: Repository Consolidation (2 days)
- [ ] Choose official GraphWriteRepositoryImpl
  - Location: `backend/repositories/sqlalchemy/graph_write_repository_impl.py`
- [ ] Deprecate duplicate
  - Location: `backend/graph/infrastructure/repositories/write.py`
- [ ] Update all imports to use official
- [ ] Run integration tests
- [ ] Verify no regression

**Acceptance Criteria**:
- Only one GraphWriteRepositoryImpl in codebase
- All tests pass
- No compile errors

### Phase 2: Persistence Consolidation (2 days)
- [ ] Define single write path
  - GraphAggregate → GraphPersistenceService → GraphWriteRepository
- [ ] Add validation to ensure all writes use this path
- [ ] Update GraphRegenerationService to use this path
- [ ] Run integration tests

**Acceptance Criteria**:
- All writes go through GraphPersistenceService
- No direct SQL INSERT in production code
- All graph_entities have case_id

### Phase 3: Builder Consolidation (2 days)
- [ ] Refactor VendorGraphBuilder to build aggregate
- [ ] Create GraphAssembler to map RUP data → GraphAggregate
- [ ] Update VendorGraphBuilder to use GraphAssembler
- [ ] Run integration tests

**Acceptance Criteria**:
- VendorGraphBuilder no longer does direct SQL INSERT
- All writes go through GraphPersistenceService
- GraphAggregate contains all data

### Phase 4: RelationshipBuilder Refactor (2 days)
- [ ] Refactor RelationshipBuilder to work with GraphAggregate
- [ ] RelationshipBuilder should only build edges (not persist)
- [ ] Edge types: shared_package, method_similarity, financial_similarity, vendor_name_similarity, same_entity_candidate
- [ ] Run integration tests

**Acceptance Criteria**:
- RelationshipBuilder does not do direct SQL INSERT
- All relationships go through GraphPersistenceService
- GraphAggregate has all edge types

### Phase 5: Legacy Removal (1 day)
- [ ] Remove duplicate GraphWriteRepositoryImpl
- [ ] Remove direct SQL INSERT from VendorGraphBuilder
- [ ] Remove direct SQL INSERT from RelationshipBuilder
- [ ] Remove deprecated GraphBuilder (in-memory)
- [ ] Remove VENDOR_COLLUSION (or migrate to shared_package)
- [ ] Run full regression tests

**Acceptance Criteria**:
- Only one graph runtime
- All tests pass
- Dashboard Intelligence shows data

## Rollback Plan

If any phase fails:

1. Revert to previous state
2. Identify root cause
3. Fix and retry

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Regression in legacy consumers | Medium | High | Comprehensive testing before removal |
| Data loss | Low | High | Backup database before each phase |
| Performance degradation | Low | Medium | Performance benchmarks |
| Integration issues | Medium | Medium | Staged rollout |
| Duplicate entities | Low | Medium | business_key validation |

## Success Criteria

- [ ] Single GraphAggregate runtime
- [ ] Single GraphWriteRepository
- [ ] All writes via repository
- [ ] graph_entities.case_id NOT NULL
- [ ] graph_entities.business_key NOT NULL
- [ ] All intelligence services working
- [ ] Dashboard Intelligence showing data
- [ ] All tests passing
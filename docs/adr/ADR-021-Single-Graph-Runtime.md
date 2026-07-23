# ADR-021: Single Graph Runtime

## Status
**PROPOSED** - Pending Discovery Completion

## Context
NEMESIS currently has 4 graph runtimes:
1. GraphAggregate (DDD) - Proposed Canonical
2. VendorGraphBuilder (Legacy)
3. RelationshipBuilder (Intelligence)
4. GraphBuilder (In-Memory)

This fragmentation causes:
- Inconsistent data
- case_id = NULL
- Duplicate repository implementations
- Hidden dependencies
- Technical debt

## Decision
Adopt **GraphAggregate** as the Single Canonical Graph Runtime.

### Rationale
1. **Enterprise DDD**: GraphAggregate follows DDD principles
2. **Validation**: Built-in validation and business rules
3. **Checksum**: Data integrity via checksum
4. **Policies**: Business policies enforced
5. **Repository Pattern**: Clean persistence layer
6. **Projection**: Built-in projection for read models
7. **Audit**: Complete audit trail
8. **Performance**: Batch operations optimized

### Consequences
**Positive**:
- Single source of truth for graph domain
- Consistent data model
- case_id always present
- business_key always present
- Clear architecture boundaries
- Easier testing
- Easier debugging

**Negative**:
- Migration effort required
- Learning curve for team
- Legacy components need refactoring
- Temporary dual runtime during migration

### Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Keep VendorGraphBuilder | No migration | No validation, no checksum, bypass architecture | REJECTED |
| Keep RelationshipBuilder | Already working | No domain model, direct SQL | REJECTED |
| Keep GraphBuilder | Simple | In-memory only, no persistence | REJECTED |
| GraphAggregate | Complete DDD | Migration required | ACCEPTED |

## Implementation Plan

### Phase 1: Repository Consolidation
- Choose official GraphWriteRepositoryImpl
- Deprecate duplicate

### Phase 2: Persistence Consolidation
- All writes via GraphPersistenceService

### Phase 3: Builder Consolidation
- VendorGraphBuilder → GraphAssembler

### Phase 4: RelationshipBuilder Refactor
- Build edges only, no persistence

### Phase 5: Legacy Removal
- Remove legacy components

## Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Architecture Lead | TBD | Pending | - |
| Backend Lead | TBD | Pending | - |
| Domain Lead | TBD | Pending | - |

## References
- GRAPH_ARCHITECTURE_DECISION.md
- GRAPH_DEPENDENCY_MAP.md
- GRAPH_MIGRATION_PLAN.md
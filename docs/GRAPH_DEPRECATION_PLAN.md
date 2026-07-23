# Graph Deprecation Plan - NEMESIS

## Deprecated Components

### 1. GraphBuilder (In-Memory)
- **Location**: `backend/graph/builder.py`
- **Status**: DEPRECATED
- **Reason**: Replaced by GraphAggregate
- **Deprecation Date**: 2026-07-21
- **Removal Date**: 2026-07-26 (Phase 5)
- **Migration**: Use GraphAggregate instead

### 2. GraphWriteRepositoryImpl (write.py)
- **Location**: `backend/graph/infrastructure/repositories/write.py`
- **Status**: DEPRECATED
- **Reason**: Duplicate implementation
- **Deprecation Date**: 2026-07-21
- **Removal Date**: 2026-07-24 (Phase 2)
- **Migration**: Use `backend/repositories/sqlalchemy/graph_write_repository_impl.py`

### 3. VendorGraphBuilder (SQL INSERT)
- **Location**: `backend/graph/engine/vendor_graph_builder.py`
- **Status**: TRANSITIONAL → DEPRECATED
- **Reason**: Bypasses architecture
- **Deprecation Date**: 2026-07-22 (Phase 3)
- **Removal Date**: 2026-07-26 (Phase 5)
- **Migration**: Refactor to build GraphAggregate, then use GraphPersistenceService

### 4. RelationshipBuilder (SQL INSERT)
- **Location**: `backend/graph/services/relationship_builder.py`
- **Status**: TRANSITIONAL → DEPRECATED
- **Reason**: Bypasses architecture
- **Deprecation Date**: 2026-07-23 (Phase 4)
- **Removal Date**: 2026-07-26 (Phase 5)
- **Migration**: Refactor to build edges, then use GraphPersistenceService

### 5. VENDOR_COLLUSION
- **Location**: graph_relationships.relationship_type
- **Status**: DEPRECATED
- **Reason**: Not used by intelligence consumers
- **Deprecation Date**: 2026-07-21
- **Removal Date**: 2026-07-26 (Phase 5)
- **Migration**: Migrate to shared_package or deprecate

### 6. rebuild_graph_rup.py
- **Location**: `backend/scripts/rebuild_graph_rup.py`
- **Status**: DEPRECATED
- **Reason**: Schema mismatch (package_id vs kode_paket)
- **Deprecation Date**: 2026-07-21
- **Removal Date**: 2026-07-26 (Phase 5)
- **Migration**: Use VendorGraphBuilder with GraphAggregate

## Deprecation Process

1. **Mark as Deprecated**
   - Add `@deprecated` decorator
   - Add warning in docstring
   - Add to GRAPH_DEPRECATION_PLAN.md

2. **Migration Period**
   - Migrate all consumers to new API
   - Update all imports
   - Run integration tests

3. **Testing**
   - Unit tests pass
   - Integration tests pass
   - Contract tests pass
   - Performance benchmarks pass

4. **Removal**
   - Delete the file/component
   - Update documentation
   - Update dependency map

## Timeline

| Component | Deprecation | Removal | Status |
|-----------|-------------|---------|--------|
| GraphBuilder (in-memory) | 2026-07-21 | 2026-07-26 | PLANNED |
| GraphWriteRepositoryImpl (write.py) | 2026-07-21 | 2026-07-24 | PLANNED |
| VendorGraphBuilder (SQL INSERT) | 2026-07-22 | 2026-07-26 | PLANNED |
| RelationshipBuilder (SQL INSERT) | 2026-07-23 | 2026-07-26 | PLANNED |
| VENDOR_COLLUSION | 2026-07-21 | 2026-07-26 | PLANNED |
| rebuild_graph_rup.py | 2026-07-21 | 2026-07-26 | PLANNED |

## Rollback Strategy

If a deprecated component needs to be restored:
1. Revert to previous version from backup
2. Document the reason
3. Update migration plan
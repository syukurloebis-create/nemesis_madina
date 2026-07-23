# \# Graph Acceptance Criteria - NEMESIS

# 

# \## Phase 1: Repository Consolidation

# 

# \### Acceptance Criteria

# \- \[ ] Only one `GraphWriteRepositoryImpl` in codebase

# \- \[ ] All imports use official repository

# \- \[ ] No compile errors

# \- \[ ] All unit tests pass

# \- \[ ] All integration tests pass

# \- \[ ] No regression in existing functionality

# 

# \### Test Coverage

# \- \[ ] Repository unit tests > 80%

# \- \[ ] Repository integration tests pass

# \- \[ ] Performance benchmarks pass

# 

# \### Rollback Criteria

# \- \[ ] Can revert to previous state within 30 minutes

# \- \[ ] No data loss

# \- \[ ] All tests pass after rollback

# 

# \---

# 

# \## Phase 2: Persistence Consolidation

# 

# \### Acceptance Criteria

# \- \[ ] All writes go through `GraphPersistenceService`

# \- \[ ] No direct SQL INSERT in production code

# \- \[ ] All `graph\_entities` have `case\_id` NOT NULL

# \- \[ ] All `graph\_entities` have `business\_key` NOT NULL

# \- \[ ] All `graph\_relationships` have `case\_id` NOT NULL

# \- \[ ] All `graph\_relationships` have valid foreign keys

# 

# \### Data Validation

# \- \[ ] No orphan relationships

# \- \[ ] No duplicate business\_key

# \- \[ ] All entities have valid `case\_id`

# \- \[ ] All relationships reference existing entities

# 

# \### Test Coverage

# \- \[ ] Persistence service unit tests > 80%

# \- \[ ] Integration tests for all write paths

# \- \[ ] Edge cases tested

# 

# \### Rollback Criteria

# \- \[ ] Can revert to previous state within 30 minutes

# \- \[ ] No data loss

# \- \[ ] All tests pass after rollback

# 

# \---

# 

# \## Phase 3: Builder Consolidation

# 

# \### Acceptance Criteria

# \- \[ ] `VendorGraphBuilder` builds `GraphAggregate`

# \- \[ ] No direct SQL INSERT in `VendorGraphBuilder`

# \- \[ ] All writes go through `GraphPersistenceService`

# \- \[ ] `GraphAssembler` maps RUP data → `GraphAggregate`

# \- \[ ] `GraphAggregate` contains all data

# 

# \### Data Validation

# \- \[ ] All vendors from RUP are in `graph\_entities`

# \- \[ ] All vendor names match exactly

# \- \[ ] No duplicate vendors

# \- \[ ] All vendors have `case\_id`

# 

# \### Test Coverage

# \- \[ ] Assembler unit tests > 80%

# \- \[ ] Builder integration tests pass

# \- \[ ] End-to-end tests pass

# 

# \### Rollback Criteria

# \- \[ ] Can revert to previous state within 1 hour

# \- \[ ] No data loss

# \- \[ ] All tests pass after rollback

# 

# \---

# 

# \## Phase 4: RelationshipBuilder Refactor

# 

# \### Acceptance Criteria

# \- \[ ] `RelationshipBuilder` builds edges only (no persistence)

# \- \[ ] All relationship types supported:

# &#x20; - \[ ] `shared\_package`

# &#x20; - \[ ] `method\_similarity`

# &#x20; - \[ ] `financial\_similarity`

# &#x20; - \[ ] `vendor\_name\_similarity`

# &#x20; - \[ ] `same\_entity\_candidate`

# \- \[ ] All edges go through `GraphPersistenceService`

# \- \[ ] No direct SQL INSERT

# 

# \### Data Validation

# \- \[ ] All expected relationships are created

# \- \[ ] No duplicate relationships

# \- \[ ] Weights are within expected range

# \- \[ ] Relationship types match intelligence expectations

# 

# \### Test Coverage

# \- \[ ] Edge builder unit tests > 80%

# \- \[ ] Integration tests for all relationship types

# \- \[ ] End-to-end tests pass

# 

# \### Rollback Criteria

# \- \[ ] Can revert to previous state within 1 hour

# \- \[ ] No data loss

# \- \[ ] All tests pass after rollback

# 

# \---

# 

# \## Phase 5: Legacy Removal

# 

# \### Acceptance Criteria

# \- \[ ] No duplicate `GraphWriteRepositoryImpl`

# \- \[ ] No direct SQL INSERT in codebase

# \- \[ ] No `VENDOR\_COLLUSION` (migrated or removed)

# \- \[ ] No deprecated `GraphBuilder` (in-memory)

# \- \[ ] All graph writes via repository

# 

# \### System Validation

# \- \[ ] Dashboard Intelligence shows data

# \- \[ ] All intelligence services working

# \- \[ ] All API endpoints working

# \- \[ ] Performance meets SLO

# \- \[ ] No regression

# 

# \### Test Coverage

# \- \[ ] Full regression test suite passes

# \- \[ ] End-to-end tests pass

# \- \[ ] Performance benchmarks pass

# \- \[ ] Security tests pass

# 

# \### Rollback Criteria

# \- \[ ] Can revert to previous state within 2 hours

# \- \[ ] No data loss

# \- \[ ] All tests pass after rollback

# 

# \---

# 

# \## Final System Validation

# 

# After all phases complete:

# 

# \### Data Integrity

# \- \[ ] `graph\_entities.case\_id` NOT NULL for all rows

# \- \[ ] `graph\_entities.business\_key` NOT NULL for all rows

# \- \[ ] `graph\_relationships.case\_id` NOT NULL for all rows

# \- \[ ] No orphan relationships

# \- \[ ] No duplicate business\_key

# 

# \### Performance

# \- \[ ] Graph build < 5 minutes for 10,000 entities

# \- \[ ] Relationship build < 10 minutes for 10,000 entities

# \- \[ ] Dashboard query < 2 seconds

# \- \[ ] API response < 500ms

# 

# \### Intelligence Services

# \- \[ ] FraudDetector returns valid patterns

# \- \[ ] ClusterDetector detects clusters

# \- \[ ] EntityGraphIntelligence returns relationships

# \- \[ ] Dashboard Intelligence shows data

# 

# \### API Endpoints

# \- \[ ] `GET /graph` returns valid graph

# \- \[ ] `GET /dashboard/intelligence` returns valid data

# \- \[ ] All endpoints return 200 OK

# \- \[ ] Error handling works

# 

# \### Documentation

# \- \[ ] Architecture documents updated

# \- \[ ] API documentation updated

# \- \[ ] Migration plan completed

# \- \[ ] Deprecation plan executed


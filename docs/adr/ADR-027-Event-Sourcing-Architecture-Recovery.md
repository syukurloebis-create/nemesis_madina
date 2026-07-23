# \# ADR-027: Event Sourcing Architecture Recovery

# 

# \## Status

# \*\*APPROVED\*\* - Based on complete evidence (A0.0 - A0.5)

# 

# \## Verified Facts

# 

# \### Event Model

# \- Fields: id, case\_id, aggregate\_id, aggregate\_type, event\_type, event\_version, event\_hash, aggregate\_hash, previous\_hash, event\_signature, signing\_key\_id, payload, metadata, commit\_position, created\_at, created\_by, tenant\_id

# \- \*\*commit\_position EXISTS\*\* - unique, indexed, global ordering

# \- \*\*event\_version\*\* - per-aggregate ordering

# \- Both ordering mechanisms are confirmed

# 

# \### commit\_position Write Path

# \- `backend/events/repository.py` - sets commit\_position via RETURNING

# \- `backend/cases/event\_store.py` - uses Event model

# \- `backend/events/store.py` - orders by commit\_position

# \- \*\*commit\_position IS populated on insert\*\*

# 

# \### EventStore API

# \- get\_events(case\_id, limit, offset) - ✅ Available

# \- get\_last\_event(case\_id) - ✅ Available

# \- get\_event\_stream(case\_id, from\_version) - ✅ Available

# \- get\_state\_at\_time(case\_id, timestamp) - ✅ Available

# \- get\_all\_from\_sequence() - ❌ NOT AVAILABLE (ProjectionRebuilder expects this)

# 

# \### ProjectionCheckpoint

# \- Fields: id, projection\_name, last\_sequence, last\_event\_id, metadata, created\_at, updated\_at

# \- \*\*NO case\_id or aggregate\_id field\*\*

# \- \*\*last\_sequence tracks GLOBAL commit\_position\*\*

# 

# \### ProjectionRebuilder Entry

# \- Signature: rebuild(resume: bool = True) - NO case\_id parameter

# \- Expects: global event stream

# 

# \### Outbox

# \- OutboxMessage - ✅ Current domain entity

# \- OutboxRepository - ✅ Current repository

# \- OutboxModel - ❌ DOES NOT EXIST (legacy)

# 

# \## Decision

# 

# \### Event Stream Contract

# \- \*\*commit\_position provides GLOBAL ordering\*\* (confirmed)

# \- \*\*event\_version provides per-aggregate ordering\*\* (confirmed)

# \- Both mechanisms exist and are populated

# 

# \### Projection Contract

# \- ProjectionRebuilder uses GLOBAL stream (commit\_position)

# \- ProjectionCheckpoint stores GLOBAL last\_sequence

# \- DashboardProjection applies events per case

# 

# \### Implementation Plan

# 

# 1\. Add `get\_events\_from\_commit\_position(from\_position, limit)` to EventStore

# 2\. Refactor ProjectionRebuilder to use new method

# 3\. Fix imports:

# &#x20;  - `EventStoreRepository` → `EventStore`

# &#x20;  - `ProjectionCheckpointModel` → `ProjectionCheckpoint`

# 4\. Update tests to use OutboxMessage, not OutboxModel

# 5\. Update tests to use current architecture

# 

# \## Acceptance Criteria

# \- \[ ] `get\_events\_from\_commit\_position()` implemented in EventStore

# \- \[ ] ProjectionRebuilder uses global commit\_position

# \- \[ ] All imports corrected

# \- \[ ] pytest --collect-only passes

# \- \[ ] Unit tests pass

# \- \[ ] Integration tests pass


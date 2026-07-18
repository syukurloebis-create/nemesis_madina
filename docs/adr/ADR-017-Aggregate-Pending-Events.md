# ADR-017: Aggregate & Pending Domain Events

## Status
**APPROVED**

## Context
NEMESIS Madina needs a consistent way to handle domain events within aggregates. Events must be recorded, stored, and published in order without race conditions or duplicate publishing.

## Decision

### 1. AggregateRoot Base Class
All aggregates extend `AggregateRoot` which provides:
- `_pending_events: list[DomainEvent[Any]]` - internal pending event storage
- `_record(event)` - internal method for recording events (not exposed to services)
- `pull_domain_events()` - consumes and returns events, clears internal list (FIFO)
- `has_pending_events()` - check if events exist

### 2. Consume Semantics
Events are consumed when pulled:
```python
events = aggregate.pull_domain_events()  # Returns tuple, clears internal list
# No separate clear() needed - consume pattern
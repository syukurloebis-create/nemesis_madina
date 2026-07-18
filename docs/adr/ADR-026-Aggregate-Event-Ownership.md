# ADR-026: Aggregate Event Ownership

**Status:** APPROVED

**Decision:** Aggregate creates pure domain events. Infrastructure adds metadata later.

**Flow:**
1. Aggregate.record_analysis() → creates DomainEvent
2. Aggregate._record(event) → stores in _pending_events
3. UnitOfWork.pull_domain_events() → collects events
4. Infrastructure → adds metadata (producer, aggregate_type, schema_version)
5. Infrastructure → publishes to EventBus or Outbox
# ADR-020: Event Publication & Outbox Compatibility

## Status
**APPROVED** - 2026-07-11

## Context
NEMESIS Madina needs an event publication mechanism that works today with InMemoryDispatcher but can evolve to support outbox pattern without changing application code.

## Decision

### 1. publish_many() as Primary API
```python
await dispatcher.publish_many(events)
# ADR-018: Repository & Unit of Work Contract

## Status
**APPROVED** - 2026-07-11

## Context
NEMESIS Madina needs a consistent data access pattern that supports transaction boundaries and event publishing.

## Decision

### 1. Repository Contract
```python
interface ICaseRepository:
    add(aggregate: CaseIntelligenceAggregate) -> None
    get(case_id: AggregateId) -> Optional[CaseIntelligenceAggregate]
    remove(aggregate: CaseIntelligenceAggregate) -> None
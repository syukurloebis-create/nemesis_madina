# Graph Ownership - NEMESIS

## Ownership Matrix

| Component | Domain | Application | Infrastructure | Runtime | Presentation |
|-----------|--------|-------------|----------------|---------|--------------|
| GraphAggregate | ✅ | - | - | - | - |
| GraphNode | ✅ | - | - | - | - |
| GraphEdge | ✅ | - | - | - | - |
| GraphPolicy | ✅ | - | - | - | - |
| GraphValidator | ✅ | - | - | - | - |
| GraphAssembler | - | ✅ | - | - | - |
| GraphRegenerationService | - | ✅ | - | - | - |
| GraphProjectionMapper | - | ✅ | - | - | - |
| GraphWriteRepository | - | - | ✅ | - | - |
| GraphReadRepository | - | - | ✅ | - | - |
| GraphMaintenanceRepository | - | - | ✅ | - | - |
| ORM Mapper | - | - | ✅ | - | - |
| VendorGraphBuilder | - | - | - | ✅ | - |
| RelationshipBuilder | - | - | - | ✅ | - |
| GraphBuilder | - | - | - | ✅ | - |
| Graph Routes | - | - | - | - | ✅ |
| Dashboard Intelligence | - | - | - | - | ✅ |

## Responsibility Mapping

### Domain Owner: Architecture Team
**Responsible for**:
- GraphAggregate design
- Business rules
- Invariants
- Domain validation
- Policy enforcement

**Decision Authority**:
- What is a valid graph
- How nodes relate to edges
- What business rules apply

---

### Application Owner: Backend Team
**Responsible for**:
- Use case orchestration
- Transaction management
- Cross-cutting concerns
- Error handling

**Decision Authority**:
- When to use which use case
- Transaction boundaries
- Error handling strategy

---

### Infrastructure Owner: Backend Team
**Responsible for**:
- Database operations
- Repository implementation
- Performance optimization
- Data integrity

**Decision Authority**:
- How data is stored
- Which database to use
- Performance tuning

---

### Runtime Owner: DevOps/SRE
**Responsible for**:
- Graph building pipelines
- Data ingestion
- Scheduled jobs
- Monitoring

**Decision Authority**:
- When to build graph
- How often to rebuild
- Data sources

---

### Presentation Owner: Frontend/Backend Team
**Responsible for**:
- API endpoints
- Response formatting
- DTO design

**Decision Authority**:
- API contract
- Response structure
- Error responses

---

## Decision Log

| Decision | Date | Owner | Status |
|----------|------|-------|--------|
| GraphAggregate as single runtime | 2026-07-21 | Architecture Team | Proposed |
| GraphPersistenceService as utility | 2026-07-21 | Architecture Team | Proposed |
| GraphWriteRepositoryImpl as official | 2026-07-21 | Backend Team | Proposed |
| Deprecate write.py | 2026-07-21 | Backend Team | Proposed |
| Refactor VendorGraphBuilder | 2026-07-21 | Backend Team | Proposed |
| Refactor RelationshipBuilder | 2026-07-21 | Intelligence Team | Proposed |
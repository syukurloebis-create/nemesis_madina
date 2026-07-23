# Graph Boundary - NEMESIS

## Layer Boundaries

### Domain Layer
**Location**: `backend/graph/domain/`

**Components**:
- `GraphAggregate` - Root aggregate
- `GraphNode` - Node entity
- `GraphEdge` - Edge entity
- `GraphPolicy` - Business rules
- `GraphChecksum` - Integrity checks
- `GraphValidator` - Validation rules

**Responsibilities**:
- Define business rules
- Enforce invariants
- No external dependencies
- Pure domain logic

**Forbidden**:
- SQL queries
- HTTP calls
- External service calls
- Database access

---

### Application Layer
**Location**: `backend/graph/application/`

**Components**:
- `GraphAssembler` - Build aggregate from DTOs
- `GraphRegenerationService` - Orchestrate graph building
- `GraphProjectionMapper` - Map aggregate to projections
- `GraphStatistics` - Build statistics

**Responsibilities**:
- Orchestrate use cases
- Coordinate domain and infrastructure
- Transaction management
- Error handling

**Forbidden**:
- Business logic (belongs in Domain)
- SQL queries (belongs in Infrastructure)
- HTTP responses (belongs in Presentation)

---

### Infrastructure Layer
**Location**: `backend/repositories/`, `backend/infrastructure/`

**Components**:
- `GraphWriteRepository` - Persistence operations
- `GraphReadRepository` - Query operations
- `GraphMaintenanceRepository` - Maintenance operations
- `ORM Mapper` - Domain ↔ ORM mapping
- `SQLAlchemy Models` - Database models

**Responsibilities**:
- Database operations
- SQL queries
- ORM mapping
- External service integration

**Forbidden**:
- Business logic
- Use case orchestration
- Domain validation

---

### Runtime Layer
**Location**: `backend/graph/engine/`, `backend/scripts/`

**Components**:
- `VendorGraphBuilder` - Build from RUP data (LEGACY)
- `RelationshipBuilder` - Build relationships (LEGACY)
- `GraphBuilder` - In-memory graph (LEGACY RUNTIME)

**Responsibilities**:
- Data extraction
- Graph construction
- Runtime orchestration

**Forbidden**:
- Direct SQL INSERT (should use Repository)
- Domain logic (should use Domain)

---

### Presentation Layer
**Location**: `backend/routers/`, `backend/graph/routes.py`

**Components**:
- `Graph Routes` - REST API endpoints
- `Dashboard Intelligence` - Graph data for dashboard
- `Graph Presenter` - DTO transformation

**Responsibilities**:
- HTTP request handling
- Response formatting
- DTO mapping

**Forbidden**:
- Business logic
- Database access
- Domain logic

---

## Cross-Layer Dependencies

### Allowed Dependencies

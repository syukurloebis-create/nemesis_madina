# \# Graph Architecture Decision - NEMESIS

# 

# \## Status

# \*\*APPROVED\*\* - Effective from 2026-07-21

# 

# \## Decision

# 

# \### Single Runtime

# \*\*Official\*\*: `GraphAggregate` (DDD Aggregate Root)

# \- Location: `backend/graph/domain/aggregate.py`

# \- Responsibilities:

# &#x20; - Root aggregate for graph domain

# &#x20; - Contains nodes (GraphNode) and edges (GraphEdge)

# &#x20; - Enforces invariant rules

# &#x20; - Single source of truth for graph domain model

# 

# \*\*Deprecated\*\*: `Graph` (in-memory)

# \- Location: `backend/graph/builder.py`

# \- Reason: Replaced by GraphAggregate

# \- Migration: All consumers to migrate to GraphAggregate

# 

# \### Single Persistence Path

# \*\*Official\*\*: `GraphAggregate → GraphPersistenceService → GraphWriteRepository`

# \- Flow:

# &#x20; 1. Build GraphAggregate

# &#x20; 2. Validate aggregate

# &#x20; 3. Save via GraphPersistenceService

# &#x20; 4. Persist via GraphWriteRepositoryImpl

# 

# \*\*Deprecated\*\*: Direct SQL INSERT

# \- Location: `vendor\_graph\_builder.py`

# \- Reason: Bypasses all architecture layers

# \- Migration: Refactor to build aggregate instead of direct SQL

# 

# \### Single Repository

# \*\*Official\*\*: `GraphWriteRepositoryImpl`

# \- Location: `backend/repositories/sqlalchemy/graph\_write\_repository\_impl.py`

# \- Features:

# &#x20; - GraphPersistenceResult

# &#x20; - RepositoryError

# &#x20; - Batch save

# &#x20; - Validation

# &#x20; - DDD compliance

# 

# \*\*Deprecated\*\*: `GraphWriteRepositoryImpl`

# \- Location: `backend/graph/infrastructure/repositories/write.py`

# \- Reason: Duplicate implementation

# \- Migration: All imports to use official repository

# 

# \### Single Application Service

# \*\*Official\*\*: `GraphRegenerationService`

# \- Location: `backend/graph/application/service.py`

# \- Responsibilities:

# &#x20; - Build graph from DTOs (via Assembler)

# &#x20; - Validate aggregate (via Validators)

# &#x20; - Apply business policies (via PolicyRegistry)

# &#x20; - Compute checksum (via ChecksumService)

# &#x20; - Persist aggregate (via Repository)

# &#x20; - Project aggregate (via ProjectionMapper)

# 

# \*\*Supporting\*\*: `GraphPersistenceService`

# \- Location: `backend/services/graph\_persistence\_service.py`

# \- Role: Simple wrapper for persistence operations

# \- Status: Utility layer, may be consolidated

# 

# \### Single Builder

# \*\*Official\*\*: `GraphAssembler`

# \- Location: `backend/graph/application/assembler.py`

# \- Responsibilities:

# &#x20; - Build GraphAggregate from DTOs

# &#x20; - Map external data to domain

# &#x20; - Single entry point for graph construction

# 

# \*\*Transitioning\*\*: `VendorGraphBuilder`

# \- Location: `backend/graph/engine/vendor\_graph\_builder.py`

# \- Current: Direct SQL INSERT (LEGACY)

# \- Target: Extract → GraphAggregate → GraphPersistenceService

# \- Status: Transitional (will be refactored)

# 

# \## Component Status Matrix

# 

# | Component | Official | Transitional | Deprecated | Action |

# |-----------|----------|--------------|------------|--------|

# | GraphAggregate | ✅ | - | - | Keep |

# | GraphPersistenceService | ✅ | - | - | Keep |

# | GraphWriteRepositoryImpl (sqlalchemy) | ✅ | - | - | Keep |

# | GraphRegenerationService | ✅ | - | - | Keep |

# | GraphAssembler | ✅ | - | - | Keep |

# | GraphBuilder (in-memory) | - | - | ❌ | Deprecate |

# | GraphWriteRepositoryImpl (write.py) | - | - | ❌ | Deprecate |

# | VendorGraphBuilder (SQL INSERT) | - | ✅ | - | Refactor |

# | VENDOR\_COLLUSION | - | ✅ | - | Migrate |

# | RelationshipBuilder (SQL INSERT) | - | ✅ | - | Refactor |

# 

# \## Migration Priority

# 

# 1\. \*\*P0\*\*: Freeze architecture (THIS DOCUMENT)

# 2\. \*\*P1\*\*: Repository consolidation (single GraphWriteRepositoryImpl)

# 3\. \*\*P2\*\*: Persistence consolidation (single write path)

# 4\. \*\*P3\*\*: Builder consolidation (VendorGraphBuilder → GraphAssembler)

# 5\. \*\*P4\*\*: RelationshipBuilder refactor (edge domain → aggregate)

# 6\. \*\*P5\*\*: Legacy removal


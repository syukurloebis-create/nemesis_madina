# Graph Dependency Map - NEMESIS

## Producer (Who Writes)

### Legacy Producers (Direct SQL INSERT)
| Component | Location | Writes | Status |
|-----------|----------|--------|--------|
| VendorGraphBuilder | `backend/graph/engine/vendor_graph_builder.py` | graph_entities, graph_relationships | ❌ LEGACY |
| RelationshipBuilder | `backend/graph/services/relationship_builder.py` | graph_relationships | ❌ LEGACY |
| rebuild_graph_rup.py | `backend/scripts/rebuild_graph_rup.py` | graph_relationships | ❌ LEGACY |

### Official Producers (Via Repository)
| Component | Location | Writes | Status |
|-----------|----------|--------|--------|
| GraphRegenerationService | `backend/graph/application/service.py` | graph_entities, graph_relationships | ✅ OFFICIAL |
| GraphPersistenceService | `backend/services/graph_persistence_service.py` | graph_entities, graph_relationships | ✅ OFFICIAL |
| GraphWriteRepositoryImpl | `backend/repositories/sqlalchemy/graph_write_repository_impl.py` | graph_entities, graph_relationships | ✅ OFFICIAL |

## Consumer (Who Reads)

### Intelligence Consumers
| Component | Location | Reads | Status |
|-----------|----------|-------|--------|
| FraudDetector | `backend/graph/intelligence/fraud_detector.py` | graph_relationships | ✅ ACTIVE |
| ClusterDetector | `backend/graph/services/cluster_detector.py` | graph_relationships | ✅ ACTIVE |
| VendorCollusionDetector | `backend/intelligence/graph/vendor_collusion_detector.py` | graph_relationships | ✅ ACTIVE |
| EntityGraphIntelligence | `backend/services/entity_graph_intelligence_service.py` | graph_relationships | ✅ ACTIVE |
| EntityEvidenceService | `backend/services/entity_evidence_service.py` | graph_relationships | ✅ ACTIVE |

### API Consumers
| Component | Location | Reads | Status |
|-----------|----------|-------|--------|
| Graph Routes | `backend/graph/routes.py` | In-memory Graph | ⚠️ LEGACY |
| Dashboard Intelligence | `backend/routers/dashboard_intelligence.py` | graph_relationships | ✅ ACTIVE |

### Runtime Consumers
| Component | Location | Reads | Status |
|-----------|----------|-------|--------|
| Startup | `backend/runtime/startup.py` | GraphBuilder | ⚠️ LEGACY |
| Health | `backend/runtime/health.py` | GraphBuilder | ⚠️ LEGACY |

## Runtime Graph Instances

### 1. DDD Runtime (Official)
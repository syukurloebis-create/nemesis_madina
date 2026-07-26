# NEMESIS V8+ Architecture Report
## Generated: Mon Jul 13 18:28:57 SEAST 2026

## 1. Executive Summary

### Current Architecture State
- **Backend**: Python FastAPI
- **Frontend**: React/TypeScript
- **Database**: PostgreSQL (via Docker)
- **Architecture Pattern**: Layered Architecture
- **Current Layers**: Router → Service → Repository → SQL

### Key Metrics
- Python files: 826
- Lines of code: 81515
- API endpoints: 275
- Services: 61
- Repositories: 19

## 2. Architecture Layers

### 2.1 Presentation Layer
```
__init__.py
alerts.py
anomalies.py
audit_logs.py
auth.py
auth_router.py
cases.py
cases_list.py
cases_risk_fixed.py
cases_risk_simple.py
copilot.py
custody.py
dashboard.py
dashboard_analytics_router.py
dashboard_case_intelligence_router.py
dashboard_entity_router.py
dashboard_intelligence.py
dashboard_intelligence_router.py
dashboard_summary.py
dashboard_summary_legacy.py
dashboard_summary_router.py
decisions.py
entities.py
entity.py
event_lineage.py
events.py
evidence.py
evidence_scoring.py
executive.py
export.py
federation.py
finding.py
finding_actions.py
finding_assignments.py
finding_intelligence.py
finding_reviews.py
finding_timeline.py
fix_anomaly.py
fix_case_prediction.py
fix_early_warning.py
fix_risk_trend.py
forensic_dashboard.py
fraud.py
fraud_detail_router.py
governance.py
graph.py
graph_nodes_fix.py
health.py
health_intelligence.py
historical.py
integrity.py
intelligence.py
investigation.py
investigations.py
lineage_nodes.py
metrics.py
metrics_fix.py
metrics_id.py
metrics_id_fixed.py
network.py
observability.py
outcome.py
predictive.py
procurement.py
procurement_api.py
procurement_list.py
provenance.py
realtime.py
rebuild.py
recommendations.py
replay.py
replay_no_auth.py
reports.py
risk.py
rup.py
rup_sqlite.py
rup_sqlite_fixed.py
snapshot.py
strategic.py
temporal.py
trust.py
upload_processor.py
upload_procurement.py
vendors.py
workflow.py
ws_debug.py
ws_gateway.py
ws_monitor.py
ws_replay.py
```

### 2.2 Application Layer
```
__init__.py
__init__.py
audit_service.py
auth_service.py
auto_verifier.py
cache.py
case_service.py
confidence_calculator.py
copilot.py
custody_service.py
dashboard_cache_events.py
dashboard_cache_manager.py
dashboard_intelligence_analytics_service.py
dashboard_intelligence_service.py
dashboard_kpi_service.py
dashboard_metrics.py
dashboard_response_factory.py
dashboard_service.py
dashboard_snapshot.py
dashboard_snapshot_builder.py
dashboard_snapshot_cache_manager.py
engine.py
entity_evidence_service.py
entity_graph_intelligence_service.py
evidence_confidence.py
evidence_intelligence.py
evidence_score.py
evidence_scoring.py
evidence_service.py
executive.py
feedback_service.py
finding_action_log_service.py
finding_assignment_service.py
finding_assignment_sla_service.py
finding_assignments.py
finding_generator.py
finding_intelligence_composer.py
finding_intelligence_engine.py
finding_intelligence_service.py
finding_lifecycle_service.py
finding_retrieval_service.py
finding_review_service.py
finding_state_machine.py
finding_timeline_normalizer.py
finding_timeline_service.py
governance.py
graph_sql.py
historical_service.py
interfaces.py
jwt_service.py
network_intelligence.py
password_validator.py
provenance.py
recovery_engine.py
recovery_service.py
replay_engine.py
replay_service.py
snapshot_service.py
status_calculator.py
temporal_engine.py
workflow_service.py
```

### 2.3 Domain Layer
```
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
aggregate_id.py
aggregate_root.py
analysis_bundle.py
application_events.py
base.py
base.py
base_uuid.py
case_aggregate.py
case_events.py
case_id.py
case_intelligence.py
case_intelligence.py
case_repository.py
case_status.py
classification.py
confidence.py
confidence.py
correlation_id.py
dashboard_summary.py
dispatcher.py
engine.py
enums.py
enums.py
event_handler.py
event_handlers.py
event_id.py
event_registry.py
event_sourcing.py
event_sourcing_repository.py
evidence.py
evidence_events.py
evidence_verification.py
exceptions.py
finding_intelligence.py
finding_with_intelligence.py
fraud_analysis.py
fraud_events.py
fraud_pattern.py
fraud_payload.py
graph_analysis.py
graph_events.py
intelligence_policy.py
intelligence_service.py
legacy_fraud_pattern.py
metadata.py
outbox.py
procurement_analysis.py
procurement_events.py
recovery_action.py
repository.py
risk.py
risk_assessment.py
risk_events.py
risk_level.py
risk_level.py
serialization.py
severity.py
snapshot.py
summary_objects.py
tenant_id.py
trace_id.py
value_objects.py
value_objects.py
```

### 2.4 Data Layer
```
base.py
consumer_repository.py
evidence_repository.py
evidence_repository_impl.py
evidence_rows.py
finding_repository.py
fraud_repository.py
fraud_repository_impl.py
fraud_rows.py
graph_repository.py
graph_repository_impl.py
graph_rows.py
procurement_repository.py
procurement_repository_impl.py
procurement_rows.py
risk_repository.py
risk_repository_impl.py
risk_rows.py
tenant_aware.py
```

### 2.5 Data Collection
```
__init__.py
collector.py
evidence_assembler.py
evidence_collector.py
exceptions.py
fraud_assembler - Salin.py
fraud_assembler.py
fraud_collector.py
graph_assembler.py
graph_collector.py
procurement_assembler.py
procurement_collector.py
registry.py
risk_assembler.py
risk_collector.py
```

### 2.6 Business Logic
```
config.py
environment_loader.py
evidence_score_calculator.py
fraud_score_calculator.py
risk_score_calculator.py
```

### 2.7 Data Mapping
```
dashboard_mapper.py
evidence_mapper.py
fraud_mapper.py
graph_mapper.py
orm_mapper.py
procurement_mapper.py
risk_mapper.py
```

### 2.8 Presentation
```
case_intelligence_presenter.py
finding_presenter.py
summary_presenter.py
```

### 2.9 Intelligence
```
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
__init__.py
alert_engine.py
anomaly.py
anomaly_detector.py
anomaly_detector.py
anomaly_engine.py
api.py
api.py
approval.py
audit.py
audit_trail_validator.py
calibration.py
calibration.py
calibration.py
calibration.py
calibrator.py
case_correlator.py
chain_of_custody.py
chain_of_custody.py
checker.py
collusion_detector.py
collusion_detector.py
collusion_detector.py
collusion_detector.py
collusion_detector.py
compliance.py
confidence_model.py
court_readiness.py
data_quality.py
detector.py
drift_detection.py
drift_monitor.py
edge_builder.py
engine.py
engine.py
ensemble.py
entity_extractor.py
entity_memory.py
entity_resolution.py
entity_schema.py
event_adapter.py
event_contract.py
evidence_hashing.py
evidence_package.py
evidence_package.py.py
evidence_registry.py
evidence_registry.py
explainability.py
explainability.py
explainability.py
explainability_engine.py
explainer.py
explanation.py
feature_engine.py
feature_store.py
feature_store.py
features.py
feedback.py
fraud_predictor.py
generator.py
graph_builder.py
graph_intelligence.py
graph_store.py
impact.py
importance.py
intelligence_engine.py
intelligence_engine.py
knowledge_graph.py
legal_report_engine.py
legalcourt_readiness.py
lime.py
lineage_intelligence.py
model_registry.py
models.py
predictor.py
procurement_risk.py
reasoning.py
relationship_graph.py
relationship_graph.py
report.py
risk_analyzer.py
risk_model.py
risk_scorer.py
role_classifier.py
scorer.py
scoring.py
service.py
service.py
shap_adapter.py
temporal_analyzer.py
temporal_scoring.py
trainer.py
triangle_detector.py
trust_model.py
unified_score.py
validator.py
validator.py
validator.py
vendor_collusion_detector.py
```

## 3. Dependency Graph

### Router → Service
```
    from backend.services.custody_service import CustodyService
    from backend.services.finding_lifecycle_service import (
    from backend.services.replay_service import ReplayService
from backend.services.auth_service import AuthService
from backend.services.copilot import copilot
from backend.services.dashboard_intelligence_analytics_service import (
from backend.services.dashboard_intelligence_service import (
from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.services.evidence_scoring import calculate_score
from backend.services.executive import ExecutiveIntelligence
from backend.services.finding_action_log_service import (
from backend.services.finding_assignment_service import (
from backend.services.finding_assignment_sla_service import (
from backend.services.finding_intelligence_service import (
from backend.services.finding_review_service import (
from backend.services.finding_timeline_service import (
from backend.services.governance import governance
from backend.services.historical_service import HistoricalService
from backend.services.interfaces import IDashboardService
from backend.services.jwt_service import JWTService
from backend.services.network_intelligence import get_key_actors, get_communities
from backend.services.provenance import get_provenance
from backend.services.replay_service import ReplayService
from backend.services.snapshot_service import SnapshotService
from entity.resolution import EntityResolutionService
from intelligence.service import IntelligenceService
```

### Service → Repository
```
from domain.event_sourcing_repository import EventSourcingRepository
```

### Service → Collector
```
    1. Collect data from all collectors (via registry + executor)
from backend.collectors.registry import CollectorRegistry
```

## 4. Database Schema
```
psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  database "nemesis" does not exist
```

## 5. Recommendations

### Current Issues
1. Engine belum menjadi layer resmi - business logic masih tersebar di Services dan Calculators
2. RiskMapper perlu diperbaiki (None vs valid data)
3. Dependency antara layer perlu dipetakan dengan lebih jelas

### Target Architecture
1. Engine menjadi layer resmi
2. Dashboard menjadi projection layer murni
3. Contract-based governance
4. Clear separation of concerns

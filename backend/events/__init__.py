# backend/events/__init__.py
from .base import BaseEvent, EventMetadata
from .registry import (
    AggregateType,
    EventType,
    register_event_schema,
    get_event_schema,
    get_all_event_schemas
)
from .schemas import *
from .store import EventStore

# Register all event schemas (auto-register)
_all_payload_classes = [
    # Case events
    CaseReportedPayload,
    CaseScreenedPayload,
    CaseAssessedPayload,
    CaseInvestigationStartedPayload,
    CaseFindingRecordedPayload,
    CaseRecommendationIssuedPayload,
    CaseFollowupStartedPayload,
    CaseClosedPayload,
    CaseCreatedPayload,
    CaseUpdatedPayload,
    CaseStatusChangedPayload,
    CasePriorityChangedPayload,
    CaseAssignedPayload,
    CaseReassignedPayload,
    CaseUnassignedPayload,
    CaseApprovedPayload,
    CaseRejectedPayload,
    CaseEscalatedToAphPayload,
    CaseRiskScoreUpdatedPayload,
    CaseTrustScoreUpdatedPayload,
    
    # Evidence events
    EvidenceAddedPayload,
    EvidenceUpdatedPayload,
    EvidenceVerifiedPayload,
    EvidenceTrustScoreUpdatedPayload,
    EvidenceArchivedPayload,
    EvidenceDeletedPayload,
    EvidenceHashValidatedPayload,
    EvidenceHashMismatchPayload,
    EvidenceChainVerifiedPayload,
    EvidenceChainBrokenPayload,
    
    # Entity events
    EntityCreatedPayload,
    EntityUpdatedPayload,
    EntityMergedPayload,
    EntityRiskScoreUpdatedPayload,
    EntityBlacklistedPayload,
    
    # Finding events
    FindingCreatedPayload,
    FindingUpdatedPayload,
    FindingApprovedPayload,
    FindingRejectedPayload,
    FindingEvidenceLinkedPayload,
    FindingEvidenceUnlinkedPayload,
    
    # Recommendation events
    RecommendationCreatedPayload,
    RecommendationUpdatedPayload,
    RecommendationApprovedPayload,
    RecommendationRejectedPayload,
    RecommendationStatusChangedPayload,
    
    # User & Security events
    UserCreatedPayload,
    UserUpdatedPayload,
    UserActivatedPayload,
    UserDeactivatedPayload,
    UserRoleChangedPayload,
    UserLoginPayload,
    UserLogoutPayload,
    AccessDeniedPayload,
    PermissionGrantedPayload,
    PermissionRevokedPayload,
    
    # Relationship events
    RelationshipCreatedPayload,
    RelationshipDiscoveredPayload,
    RelationshipVerifiedPayload,
    RelationshipRejectedPayload,
    RelationshipUpdatedPayload,
    RelationshipConfidenceUpdatedPayload,
    
    # Outcome & Recovery events
    OutcomeCreatedPayload,
    OutcomeUpdatedPayload,
    RecoveryTargetSetPayload,
    RecoveryActionRecordedPayload,
    RecoveryTargetAchievedPayload,
    
    # Data lineage events
    DataImportedPayload,
    DataTransformedPayload,
    DataValidatedPayload,
    DataRejectedPayload,
    
    # Model governance events
    ModelRegisteredPayload,
    ModelValidatedPayload,
    ModelDeployedPayload,
    ModelRetiredPayload,
]

# Register schemas (simplified - actual implementation would map to EventType)
__all__ = [
    "BaseEvent",
    "EventMetadata",
    "AggregateType",
    "EventType",
    "EventStore",
    "register_event_schema",
    "get_event_schema",
    "get_all_event_schemas",
]
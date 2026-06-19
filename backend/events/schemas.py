# backend/events/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid


# ============================================================
# CASE EVENT PAYLOADS (20 events)
# ============================================================

class CaseReportedPayload(BaseModel):
    case_id: uuid.UUID
    source_type: str  # PUBLIC_REPORT, AUDIT, INTELLIGENCE, PROCUREMENT_ALERT, MANUAL
    source_reference: Optional[str] = None
    reporter_info: Optional[Dict[str, Any]] = None
    reported_at: datetime


class CaseScreenedPayload(BaseModel):
    case_id: uuid.UUID
    screening_result: str  # PASS, NEEDS_ASSESSMENT, REJECTED
    screening_notes: Optional[str] = None
    screened_by: uuid.UUID
    screened_at: datetime


class CaseAssessedPayload(BaseModel):
    case_id: uuid.UUID
    assessment_result: str  # INVESTIGATE, MONITOR, CLOSE
    priority: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float = Field(ge=0, le=100)
    assessed_by: uuid.UUID
    assessed_at: datetime


class CaseInvestigationStartedPayload(BaseModel):
    case_id: uuid.UUID
    investigation_scope: Optional[str] = None
    started_by: uuid.UUID
    started_at: datetime


class CaseFindingRecordedPayload(BaseModel):
    case_id: uuid.UUID
    finding_id: uuid.UUID
    recorded_by: uuid.UUID
    recorded_at: datetime


class CaseRecommendationIssuedPayload(BaseModel):
    case_id: uuid.UUID
    recommendation_id: uuid.UUID
    issued_by: uuid.UUID
    issued_at: datetime


class CaseFollowupStartedPayload(BaseModel):
    case_id: uuid.UUID
    followup_plan: Optional[str] = None
    started_by: uuid.UUID
    started_at: datetime


class CaseClosedPayload(BaseModel):
    case_id: uuid.UUID
    outcome_id: uuid.UUID
    closed_by: uuid.UUID
    closed_at: datetime
    reason: Optional[str] = None


class CaseCreatedPayload(BaseModel):
    case_id: uuid.UUID
    case_number: str
    title: str
    description: Optional[str] = None
    priority: str = "MEDIUM"
    created_by: uuid.UUID
    created_at: datetime


class CaseUpdatedPayload(BaseModel):
    case_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class CaseStatusChangedPayload(BaseModel):
    case_id: uuid.UUID
    old_status: str
    new_status: str
    changed_by: uuid.UUID
    changed_at: datetime
    reason: Optional[str] = None


class CasePriorityChangedPayload(BaseModel):
    case_id: uuid.UUID
    old_priority: str
    new_priority: str
    changed_by: uuid.UUID
    changed_at: datetime


class CaseAssignedPayload(BaseModel):
    case_id: uuid.UUID
    assigned_to: uuid.UUID
    assigned_by: uuid.UUID
    assigned_at: datetime
    assignment_note: Optional[str] = None


class CaseReassignedPayload(BaseModel):
    case_id: uuid.UUID
    old_assignee: uuid.UUID
    new_assignee: uuid.UUID
    reassigned_by: uuid.UUID
    reassigned_at: datetime
    reason: Optional[str] = None


class CaseUnassignedPayload(BaseModel):
    case_id: uuid.UUID
    unassigned_by: uuid.UUID
    unassigned_at: datetime
    reason: Optional[str] = None


class CaseApprovedPayload(BaseModel):
    case_id: uuid.UUID
    approved_by: uuid.UUID
    approved_at: datetime
    approval_level: str  # IRBAN, INSPEKTUR
    notes: Optional[str] = None


class CaseRejectedPayload(BaseModel):
    case_id: uuid.UUID
    rejected_by: uuid.UUID
    rejected_at: datetime
    rejection_reason: str


class CaseEscalatedToAphPayload(BaseModel):
    case_id: uuid.UUID
    aph_institution: str  # KEJAKSAAN, KEPOLISIAN, BPKP, BPK
    escalated_by: uuid.UUID
    escalated_at: datetime
    case_materials: Optional[List[str]] = None


class CaseRiskScoreUpdatedPayload(BaseModel):
    case_id: uuid.UUID
    old_score: float = Field(ge=0, le=100)
    new_score: float = Field(ge=0, le=100)
    assessment_id: uuid.UUID
    calculated_at: datetime


class CaseTrustScoreUpdatedPayload(BaseModel):
    case_id: uuid.UUID
    old_score: float = Field(ge=0, le=100)
    new_score: float = Field(ge=0, le=100)
    calculated_at: datetime


# ============================================================
# EVIDENCE EVENT PAYLOADS (10 events)
# ============================================================

class EvidenceAddedPayload(BaseModel):
    evidence_id: uuid.UUID
    case_id: uuid.UUID
    evidence_type: str  # DOCUMENT, PHOTO, VIDEO, INTERVIEW, FINANCIAL_RECORD, PROCUREMENT_RECORD, EXTERNAL_INTELLIGENCE
    filename: str
    file_hash: str
    file_size: int
    uploaded_by: uuid.UUID
    uploaded_at: datetime


class EvidenceUpdatedPayload(BaseModel):
    evidence_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class EvidenceVerifiedPayload(BaseModel):
    evidence_id: uuid.UUID
    verified_by: uuid.UUID
    verified_at: datetime
    trust_score: float = Field(ge=0, le=100)


class EvidenceTrustScoreUpdatedPayload(BaseModel):
    evidence_id: uuid.UUID
    old_score: float = Field(ge=0, le=100)
    new_score: float = Field(ge=0, le=100)
    calculated_at: datetime


class EvidenceArchivedPayload(BaseModel):
    evidence_id: uuid.UUID
    archived_by: uuid.UUID
    archived_at: datetime
    reason: Optional[str] = None
    retention_until: Optional[datetime] = None


class EvidenceDeletedPayload(BaseModel):
    evidence_id: uuid.UUID
    deleted_by: uuid.UUID
    deleted_at: datetime
    reason: Optional[str] = None


class EvidenceHashValidatedPayload(BaseModel):
    evidence_id: uuid.UUID
    validated_hash: str
    validated_by: uuid.UUID
    validated_at: datetime


class EvidenceHashMismatchPayload(BaseModel):
    evidence_id: uuid.UUID
    expected_hash: str
    actual_hash: str
    detected_at: datetime
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class EvidenceChainVerifiedPayload(BaseModel):
    evidence_id: uuid.UUID
    verification_result: bool
    verified_by: uuid.UUID
    verified_at: datetime


class EvidenceChainBrokenPayload(BaseModel):
    evidence_id: uuid.UUID
    broken_at: datetime
    reason: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


# ============================================================
# ENTITY EVENT PAYLOADS (5 events)
# ============================================================

class EntityCreatedPayload(BaseModel):
    entity_id: uuid.UUID
    entity_type: str  # VENDOR, OFFICIAL, COMPANY, PERSON, ADDRESS, BANK_ACCOUNT, OTHER
    name: str
    identifier: Optional[str] = None
    source_system: str
    created_at: datetime


class EntityUpdatedPayload(BaseModel):
    entity_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class EntityMergedPayload(BaseModel):
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    merged_by: uuid.UUID
    merged_at: datetime
    reason: Optional[str] = None


class EntityRiskScoreUpdatedPayload(BaseModel):
    entity_id: uuid.UUID
    old_score: float = Field(ge=0, le=100)
    new_score: float = Field(ge=0, le=100)
    assessment_id: uuid.UUID
    calculated_at: datetime


class EntityBlacklistedPayload(BaseModel):
    entity_id: uuid.UUID
    blacklisted_by: uuid.UUID
    blacklisted_at: datetime
    reason: str


# ============================================================
# FINDING EVENT PAYLOADS (6 events)
# ============================================================

class FindingCreatedPayload(BaseModel):
    finding_id: uuid.UUID
    case_id: uuid.UUID
    finding_type: str  # MARK_UP, FICTIVE, COLLUSION, CONFLICT_OF_INTEREST, SPLIT_PROCUREMENT, OTHER
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    created_by: uuid.UUID
    created_at: datetime


class FindingUpdatedPayload(BaseModel):
    finding_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class FindingApprovedPayload(BaseModel):
    finding_id: uuid.UUID
    approved_by: uuid.UUID
    approved_at: datetime
    notes: Optional[str] = None


class FindingRejectedPayload(BaseModel):
    finding_id: uuid.UUID
    rejected_by: uuid.UUID
    rejected_at: datetime
    rejection_reason: str


class FindingEvidenceLinkedPayload(BaseModel):
    finding_id: uuid.UUID
    evidence_id: uuid.UUID
    linked_by: uuid.UUID
    linked_at: datetime


class FindingEvidenceUnlinkedPayload(BaseModel):
    finding_id: uuid.UUID
    evidence_id: uuid.UUID
    unlinked_by: uuid.UUID
    unlinked_at: datetime


# ============================================================
# RECOMMENDATION EVENT PAYLOADS (5 events)
# ============================================================

class RecommendationCreatedPayload(BaseModel):
    recommendation_id: uuid.UUID
    finding_id: uuid.UUID
    recommendation_type: str  # REVIEW, AUDIT, ESCALATE, RECOVER, POLICY_CHANGE, OTHER
    target_entity: Optional[str] = None
    description: str
    due_date: Optional[datetime] = None
    created_at: datetime


class RecommendationUpdatedPayload(BaseModel):
    recommendation_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class RecommendationApprovedPayload(BaseModel):
    recommendation_id: uuid.UUID
    approved_by: uuid.UUID
    approved_at: datetime


class RecommendationRejectedPayload(BaseModel):
    recommendation_id: uuid.UUID
    rejected_by: uuid.UUID
    rejected_at: datetime
    reason: str


class RecommendationStatusChangedPayload(BaseModel):
    recommendation_id: uuid.UUID
    old_status: str  # PENDING, IN_PROGRESS, COMPLETED, OVERDUE, CANCELLED
    new_status: str
    changed_by: uuid.UUID
    changed_at: datetime
    reason: Optional[str] = None


# ============================================================
# USER & SECURITY EVENT PAYLOADS (10 events)
# ============================================================

class UserCreatedPayload(BaseModel):
    user_id: uuid.UUID
    username: str
    email: str
    role: str  # INVESTIGATOR, IRBAN, INSPEKTUR, ADMIN, EXECUTIVE
    organizational_unit: Optional[str] = None
    created_at: datetime


class UserUpdatedPayload(BaseModel):
    user_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class UserActivatedPayload(BaseModel):
    user_id: uuid.UUID
    activated_by: uuid.UUID
    activated_at: datetime


class UserDeactivatedPayload(BaseModel):
    user_id: uuid.UUID
    deactivated_by: uuid.UUID
    deactivated_at: datetime
    reason: Optional[str] = None


class UserRoleChangedPayload(BaseModel):
    user_id: uuid.UUID
    old_role: str
    new_role: str
    changed_by: uuid.UUID
    changed_at: datetime


class UserLoginPayload(BaseModel):
    user_id: uuid.UUID
    username: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_at: datetime
    success: bool


class UserLogoutPayload(BaseModel):
    user_id: uuid.UUID
    logout_at: datetime


class AccessDeniedPayload(BaseModel):
    user_id: uuid.UUID
    resource: str
    action: str
    ip_address: Optional[str] = None
    attempted_at: datetime
    reason: str


class PermissionGrantedPayload(BaseModel):
    user_id: uuid.UUID
    permission: str
    granted_by: uuid.UUID
    granted_at: datetime


class PermissionRevokedPayload(BaseModel):
    user_id: uuid.UUID
    permission: str
    revoked_by: uuid.UUID
    revoked_at: datetime


# ============================================================
# RELATIONSHIP EVENT PAYLOADS (6 events)
# ============================================================

class RelationshipCreatedPayload(BaseModel):
    relationship_id: uuid.UUID
    case_id: uuid.UUID
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relationship_type: str  # OWNER, DIRECTOR, SHAREHOLDER, FAMILY, SAME_ADDRESS, SAME_PHONE, SAME_BANK_ACCOUNT, PROCUREMENT_PARTICIPANT, CONTRACT_SIGNATORY
    confidence_score: float = Field(ge=0, le=100)
    created_by: uuid.UUID
    created_at: datetime


class RelationshipDiscoveredPayload(BaseModel):
    relationship_id: uuid.UUID
    case_id: uuid.UUID
    source_entity_id: uuid.UUID
    target_entity_id: uuid.UUID
    relationship_type: str
    confidence_score: float = Field(ge=0, le=100)
    discovery_method: str  # GRAPH_ALGORITHM, NLP, RULE_BASED, AI
    discovered_at: datetime


class RelationshipVerifiedPayload(BaseModel):
    relationship_id: uuid.UUID
    verified_by: uuid.UUID
    verified_at: datetime
    confidence_score_new: float = Field(ge=0, le=100)


class RelationshipRejectedPayload(BaseModel):
    relationship_id: uuid.UUID
    rejected_by: uuid.UUID
    rejected_at: datetime
    rejection_reason: str


class RelationshipUpdatedPayload(BaseModel):
    relationship_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_at: datetime


class RelationshipConfidenceUpdatedPayload(BaseModel):
    relationship_id: uuid.UUID
    old_confidence: float = Field(ge=0, le=100)
    new_confidence: float = Field(ge=0, le=100)
    updated_at: datetime


# ============================================================
# OUTCOME & RECOVERY EVENT PAYLOADS (5 events)
# ============================================================

class OutcomeCreatedPayload(BaseModel):
    outcome_id: uuid.UUID
    case_id: uuid.UUID
    estimated_loss: Optional[Decimal] = None
    referred_to_aph: bool = False
    aph_institution: Optional[str] = None
    closed_at: datetime


class OutcomeUpdatedPayload(BaseModel):
    outcome_id: uuid.UUID
    fields_updated: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: uuid.UUID
    updated_at: datetime


class RecoveryTargetSetPayload(BaseModel):
    outcome_id: uuid.UUID
    target_amount: Decimal
    target_date: datetime
    set_by: uuid.UUID
    set_at: datetime


class RecoveryActionRecordedPayload(BaseModel):
    recovery_id: uuid.UUID
    outcome_id: uuid.UUID
    amount: Decimal
    recovery_method: str  # CASH, ASSET_RETURN, CONTRACT_ADJUSTMENT, OTHER
    recovered_at: datetime


class RecoveryTargetAchievedPayload(BaseModel):
    outcome_id: uuid.UUID
    total_recovered: Decimal
    achieved_at: datetime


# ============================================================
# DATA LINEAGE EVENT PAYLOADS (4 events)
# ============================================================

class DataImportedPayload(BaseModel):
    import_id: uuid.UUID
    source_id: uuid.UUID
    records_count: int
    imported_at: datetime
    status: str  # SUCCESS, PARTIAL, FAILED


class DataTransformedPayload(BaseModel):
    import_id: uuid.UUID
    transformation_rule: str
    records_affected: int
    transformed_at: datetime


class DataValidatedPayload(BaseModel):
    import_id: uuid.UUID
    validation_result: bool
    errors_count: int
    validated_at: datetime


class DataRejectedPayload(BaseModel):
    import_id: uuid.UUID
    rejection_reason: str
    rejected_at: datetime


# ============================================================
# MODEL GOVERNANCE EVENT PAYLOADS (4 events)
# ============================================================

class ModelRegisteredPayload(BaseModel):
    model_id: uuid.UUID
    model_name: str
    model_type: str  # RISK, DETECTION, PREDICTION
    version: str
    registered_at: datetime
    registered_by: uuid.UUID


class ModelValidatedPayload(BaseModel):
    model_id: uuid.UUID
    validation_result: bool
    accuracy: float
    precision: float
    recall: float
    validated_at: datetime


class ModelDeployedPayload(BaseModel):
    model_id: uuid.UUID
    deployed_at: datetime
    deployed_by: uuid.UUID
    environment: str  # DEVELOPMENT, STAGING, PRODUCTION


class ModelRetiredPayload(BaseModel):
    model_id: uuid.UUID
    retired_at: datetime
    retired_by: uuid.UUID
    reason: str
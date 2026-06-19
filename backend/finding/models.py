from enum import Enum
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass
import uuid


class FindingType(str, Enum):
    MARK_UP = "MARK_UP"
    FICTIVE = "FICTIVE"
    COLLUSION = "COLLUSION"
    CONFLICT_OF_INTEREST = "CONFLICT_OF_INTEREST"
    SPLIT_PROCUREMENT = "SPLIT_PROCUREMENT"
    OTHER = "OTHER"


class FindingSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingStatus(str, Enum):
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class Finding:
    finding_id: uuid.UUID
    case_id: uuid.UUID
    finding_type: FindingType
    severity: FindingSeverity
    description: str
    evidence_ids: List[uuid.UUID]
    status: FindingStatus
    created_by: uuid.UUID
    created_at: datetime
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "finding_id": str(self.finding_id),
            "case_id": str(self.case_id),
            "finding_type": self.finding_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "evidence_ids": [str(eid) for eid in self.evidence_ids],
            "status": self.status.value,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat(),
            "approved_by": str(self.approved_by) if self.approved_by else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejection_reason": self.rejection_reason
        }


class FindingService:
    def __init__(self, db_session):
        self.session = db_session
        self._findings = {}
    
    async def create_finding(
        self,
        case_id: uuid.UUID,
        finding_type: FindingType,
        severity: FindingSeverity,
        description: str,
        evidence_ids: List[uuid.UUID],
        created_by: uuid.UUID
    ) -> Finding:
        finding = Finding(
            finding_id=uuid.uuid4(),
            case_id=case_id,
            finding_type=finding_type,
            severity=severity,
            description=description,
            evidence_ids=evidence_ids,
            status=FindingStatus.DRAFT,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        self._findings[finding.finding_id] = finding
        return finding
    
    async def approve_finding(
        self,
        finding_id: uuid.UUID,
        approved_by: uuid.UUID
    ) -> Optional[Finding]:
        finding = self._findings.get(finding_id)
        if finding and finding.status == FindingStatus.DRAFT:
            finding.status = FindingStatus.APPROVED
            finding.approved_by = approved_by
            finding.approved_at = datetime.utcnow()
        return finding
    
    async def reject_finding(
        self,
        finding_id: uuid.UUID,
        rejected_by: uuid.UUID,
        reason: str
    ) -> Optional[Finding]:
        finding = self._findings.get(finding_id)
        if finding and finding.status == FindingStatus.DRAFT:
            finding.status = FindingStatus.REJECTED
            finding.approved_by = rejected_by
            finding.approved_at = datetime.utcnow()
            finding.rejection_reason = reason
        return finding
    
    async def get_findings_by_case(self, case_id: uuid.UUID) -> List[Finding]:
        return [f for f in self._findings.values() if f.case_id == case_id]

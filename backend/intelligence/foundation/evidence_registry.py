"""
Evidence Registry
Mengelola semua evidence dengan integritas dan lineage
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvidenceRecord:
    """Record evidence dengan integritas"""
    id: UUID = field(default_factory=uuid4)
    case_id: UUID = None
    source: str = ""
    evidence_type: str = "document"
    content: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""
    verified: bool = False
    trust_score: float = 0.0
    lineage: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.hash and self.content:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Compute hash dari content"""
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def verify(self) -> bool:
        """Verifikasi integritas evidence"""
        computed_hash = self.compute_hash()
        self.verified = computed_hash == self.hash
        self.updated_at = datetime.now()
        return self.verified

    def add_lineage(self, event: str, metadata: Dict[str, Any]) -> None:
        """Tambahkan lineage entry"""
        self.lineage.append({
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        })
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Konversi ke dictionary"""
        return {
            "id": str(self.id),
            "case_id": str(self.case_id) if self.case_id else None,
            "source": self.source,
            "evidence_type": self.evidence_type,
            "content": self.content,
            "hash": self.hash,
            "verified": self.verified,
            "trust_score": self.trust_score,
            "lineage": self.lineage,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class EvidenceRegistry:
    """Registry untuk semua evidence"""

    def __init__(self):
        self.evidences: Dict[str, EvidenceRecord] = {}
        self.case_evidence_index: Dict[str, List[str]] = {}

    def register_evidence(
        self,
        case_id: UUID,
        source: str,
        evidence_type: str,
        content: Dict[str, Any],
        trust_score: float = 0.0
    ) -> EvidenceRecord:
        """Register evidence baru"""
        evidence = EvidenceRecord(
            case_id=case_id,
            source=source,
            evidence_type=evidence_type,
            content=content,
            trust_score=trust_score
        )
        self.evidences[str(evidence.id)] = evidence

        # Index by case
        case_key = str(case_id)
        if case_key not in self.case_evidence_index:
            self.case_evidence_index[case_key] = []
        self.case_evidence_index[case_key].append(str(evidence.id))

        logger.info(f"Evidence registered: {evidence.id} (case: {case_id})")
        return evidence

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceRecord]:
        """Get evidence by ID"""
        return self.evidences.get(evidence_id)

    def get_evidence_by_case(self, case_id: str) -> List[EvidenceRecord]:
        """Get all evidence for a case"""
        evidence_ids = self.case_evidence_index.get(case_id, [])
        return [self.evidences[eid] for eid in evidence_ids if eid in self.evidences]

    def verify_evidence(self, evidence_id: str) -> bool:
        """Verify evidence integrity"""
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False
        return evidence.verify()

    def update_trust_score(self, evidence_id: str, new_score: float) -> bool:
        """Update trust score"""
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False
        evidence.trust_score = new_score
        evidence.updated_at = datetime.now()
        return True

    def add_lineage(
        self,
        evidence_id: str,
        event: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add lineage to evidence"""
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False
        evidence.add_lineage(event, metadata)
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total = len(self.evidences)
        verified = sum(1 for e in self.evidences.values() if e.verified)
        by_type = {}
        by_source = {}

        for evidence in self.evidences.values():
            by_type[evidence.evidence_type] = by_type.get(evidence.evidence_type, 0) + 1
            by_source[evidence.source] = by_source.get(evidence.source, 0) + 1

        return {
            "total_evidence": total,
            "verified_evidence": verified,
            "verification_rate": verified / total if total > 0 else 0,
            "by_type": by_type,
            "by_source": by_source,
            "cases_with_evidence": len(self.case_evidence_index)
        }


# Singleton instance
evidence_registry = EvidenceRegistry()
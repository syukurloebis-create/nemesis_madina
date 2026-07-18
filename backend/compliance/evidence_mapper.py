"""
Evidence Mapper
Mapping evidence ke requirement APIP
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class EvidenceMapping:
    """Mapping evidence ke requirement"""
    requirement_id: str
    evidence_type: str
    description: str
    file_paths: List[str] = field(default_factory=list)
    validation_method: str = "manual"
    validation_status: str = "pending"
    validated_at: Optional[datetime] = None
    validated_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "evidence_type": self.evidence_type,
            "description": self.description,
            "file_paths": self.file_paths,
            "validation_method": self.validation_method,
            "validation_status": self.validation_status,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "validated_by": self.validated_by
        }


class EvidenceMapper:
    """
    Evidence Mapper
    Mapping evidence ke requirement APIP
    """

    def __init__(self):
        self.mappings: Dict[str, List[EvidenceMapping]] = {}
        self._init_mappings()

    def _init_mappings(self) -> None:
        """Initialize evidence mappings"""
        mappings = [
            # Risk Management
            {
                "requirement_id": "APIP-001",
                "evidence_type": "Risk Assessment",
                "description": "Risk reasoning engine implementation",
                "file_paths": [
                    "backend/intelligence/reasoning/engine.py",
                    "backend/intelligence/reasoning/explainability.py"
                ]
            },
            {
                "requirement_id": "APIP-002",
                "evidence_type": "Risk Mitigation",
                "description": "Recommendation engine",
                "file_paths": [
                    "backend/services/recommendation/engine.py"
                ]
            },
            {
                "requirement_id": "APIP-003",
                "evidence_type": "Risk Monitoring",
                "description": "Real-time risk monitoring",
                "file_paths": [
                    "backend/monitoring/performance.py"
                ]
            },
            # Audit
            {
                "requirement_id": "APIP-004",
                "evidence_type": "Audit Trail",
                "description": "Audit logging system",
                "file_paths": [
                    "backend/audit/audit_logger.py"
                ]
            },
            {
                "requirement_id": "APIP-005",
                "evidence_type": "Evidence Management",
                "description": "Evidence registry",
                "file_paths": [
                    "backend/intelligence/foundation/evidence_registry.py"
                ]
            },
            {
                "requirement_id": "APIP-006",
                "evidence_type": "Chain of Custody",
                "description": "Chain of custody tracking",
                "file_paths": [
                    "backend/evidence/custody.py"
                ]
            },
            # Integrity
            {
                "requirement_id": "APIP-007",
                "evidence_type": "Data Integrity",
                "description": "Event sourcing integrity",
                "file_paths": [
                    "backend/events/verifier.py"
                ]
            },
            {
                "requirement_id": "APIP-008",
                "evidence_type": "Cryptographic Validation",
                "description": "Cryptographic hash validation",
                "file_paths": [
                    "backend/events/hasher.py"
                ]
            },
            {
                "requirement_id": "APIP-009",
                "evidence_type": "Access Control",
                "description": "RBAC implementation",
                "file_paths": [
                    "backend/security/rbac.py"
                ]
            },
            # Intelligence
            {
                "requirement_id": "APIP-010",
                "evidence_type": "Fraud Detection",
                "description": "Fraud prediction model",
                "file_paths": [
                    "backend/intelligence/predictive/fraud_predictor.py"
                ]
            },
            {
                "requirement_id": "APIP-011",
                "evidence_type": "Predictive Analytics",
                "description": "Anomaly detection",
                "file_paths": [
                    "backend/intelligence/predictive/anomaly_detector.py"
                ]
            },
            {
                "requirement_id": "APIP-012",
                "evidence_type": "Explainable AI",
                "description": "Explainability engine",
                "file_paths": [
                    "backend/intelligence/reasoning/explainability.py"
                ]
            },
            # Reporting
            {
                "requirement_id": "APIP-013",
                "evidence_type": "Comprehensive Reports",
                "description": "Report generation",
                "file_paths": [
                    "backend/compliance/apip.py"
                ]
            },
            {
                "requirement_id": "APIP-014",
                "evidence_type": "Decision Support",
                "description": "Decision engine",
                "file_paths": [
                    "backend/intelligence/decision/engine.py"
                ]
            },
            {
                "requirement_id": "APIP-015",
                "evidence_type": "Performance Measurement",
                "description": "Impact tracking",
                "file_paths": [
                    "backend/intelligence/decision/impact.py"
                ]
            }
        ]

        for mapping in mappings:
            self.add_mapping(EvidenceMapping(**mapping))

    def add_mapping(self, mapping: EvidenceMapping) -> None:
        """Add evidence mapping"""
        if mapping.requirement_id not in self.mappings:
            self.mappings[mapping.requirement_id] = []
        self.mappings[mapping.requirement_id].append(mapping)

    def get_mappings(self, requirement_id: str) -> List[EvidenceMapping]:
        """Get mappings for requirement"""
        return self.mappings.get(requirement_id, [])

    def get_all_mappings(self) -> Dict[str, List[EvidenceMapping]]:
        """Get all mappings"""
        return self.mappings

    def validate_evidence(self, requirement_id: str, evidence_type: str) -> bool:
        """Validate evidence exists"""
        mappings = self.get_mappings(requirement_id)
        for mapping in mappings:
            if mapping.evidence_type == evidence_type:
                # Check if files exist
                import os
                for file_path in mapping.file_paths:
                    if not os.path.exists(file_path):
                        mapping.validation_status = "missing"
                        return False
                mapping.validation_status = "valid"
                mapping.validated_at = datetime.now()
                return True
        return False

    def get_compliance_evidence(self) -> Dict[str, Any]:
        """Get all compliance evidence"""
        evidence = {}
        for req_id, mappings in self.mappings.items():
            evidence[req_id] = [m.to_dict() for m in mappings]
        return evidence


# Singleton instance
evidence_mapper = EvidenceMapper()
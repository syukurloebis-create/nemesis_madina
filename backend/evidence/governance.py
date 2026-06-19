# backend/evidence/governance.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .classification import (
    EvidenceType, EvidenceSource, EvidenceFormat,
    EvidenceClassificationLevel, get_classification_registry
)
from .trust_score import get_trust_score_engine, TrustLevel
from .custody import get_custody_service, CustodyAction
from .retention import get_retention_engine


class EvidenceGovernanceService:
    """Integrated service for evidence governance"""
    
    def __init__(self):
        self.classification_registry = get_classification_registry()
        self.trust_score_engine = get_trust_score_engine()
        self.custody_service = get_custody_service()
        self.retention_engine = get_retention_engine()
    
    async def classify_evidence(
        self,
        evidence_id: uuid.UUID,
        evidence_type: EvidenceType,
        source_type: EvidenceSource,
        format: EvidenceFormat,
        classification_level: EvidenceClassificationLevel,
        uploaded_by: uuid.UUID,
        uploaded_by_name: str,
        uploaded_by_role: str
    ) -> Dict[str, Any]:
        """Classify evidence and initialize governance"""
        
        # Get classification definition
        classification = self.classification_registry.get_classification(evidence_type)
        
        if not classification:
            return {"error": f"Unknown evidence type: {evidence_type}"}
        
        # Record custody event for upload
        custody_event = self.custody_service.record_event(
            evidence_id=evidence_id,
            action=CustodyAction.UPLOADED,
            actor_id=uploaded_by,
            actor_name=uploaded_by_name,
            actor_role=uploaded_by_role,
            notes=f"Evidence uploaded and classified as {evidence_type.value}"
        )
        
        # Calculate initial trust score (will be updated after verification)
        # For now, create placeholder
        trust_score = None
        
        # Determine retention policy
        retention_date = self.retention_engine.get_retention_date(
            evidence_type=evidence_type.value,
            classification=classification_level.value,
            created_at=datetime.utcnow(),
            case_status="ACTIVE",
            risk_level="MEDIUM",
            legal_hold=False
        )
        
        return {
            "evidence_id": str(evidence_id),
            "evidence_type": evidence_type.value,
            "classification": classification.to_dict(),
            "custody_event": custody_event.to_dict(),
            "retention_date": retention_date.isoformat(),
            "trust_score": trust_score,
            "status": "CLASSIFIED"
        }
    
    async def verify_evidence(
        self,
        evidence_id: uuid.UUID,
        verified_by: uuid.UUID,
        verified_by_name: str,
        verified_by_role: str,
        hash_validated: bool,
        hash_match: bool,
        file_metadata: Dict,
        declared_metadata: Dict
    ) -> Dict[str, Any]:
        """Verify evidence and calculate trust score"""
        
        # Get custody events
        chain = self.custody_service.get_chain(evidence_id)
        custody_events = chain.get_events()
        
        # Calculate trust score
        trust_score_result = self.trust_score_engine.calculate(
            evidence_id=evidence_id,
            source_type="INTERNAL",  # TODO: Get from evidence record
            source_trust_level="HIGH",  # TODO: Get from evidence record
            hash_validated=hash_validated,
            hash_match=hash_match,
            custody_events=[e.to_dict() for e in custody_events],
            current_holder=chain.get_current_holder() or verified_by_name,
            file_metadata=file_metadata,
            declared_metadata=declared_metadata,
            uploaded_at=datetime.utcnow(),  # TODO: Get from evidence record
            modified_at=None
        )
        
        # Record verification custody event
        self.custody_service.record_event(
            evidence_id=evidence_id,
            action=CustodyAction.VERIFIED,
            actor_id=verified_by,
            actor_name=verified_by_name,
            actor_role=verified_by_role,
            notes=f"Evidence verified - Trust score: {trust_score_result['total_score']}"
        )
        
        return {
            "evidence_id": str(evidence_id),
            "trust_score": trust_score_result,
            "verified_by": str(verified_by),
            "verified_at": datetime.utcnow().isoformat()
        }
    
    async def transfer_evidence(
        self,
        evidence_id: uuid.UUID,
        to_holder: str,
        transferred_by: uuid.UUID,
        transferred_by_name: str,
        transferred_by_role: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transfer evidence to another holder"""
        
        chain = self.custody_service.get_chain(evidence_id)
        current_holder = chain.get_current_holder()
        
        if not current_holder:
            return {"error": "Cannot determine current holder"}
        
        events = self.custody_service.transfer_evidence(
            evidence_id=evidence_id,
            from_holder=current_holder,
            to_holder=to_holder,
            actor_id=transferred_by,
            actor_name=transferred_by_name,
            actor_role=transferred_by_role,
            notes=notes
        )
        
        return {
            "evidence_id": str(evidence_id),
            "from_holder": current_holder,
            "to_holder": to_holder,
            "transfer_events": [e.to_dict() for e in events],
            "transferred_at": datetime.utcnow().isoformat()
        }
    
    async def get_evidence_report(
        self,
        evidence_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get complete governance report for evidence"""
        
        # Get custody chain
        chain = self.custody_service.get_full_chain(evidence_id)
        
        # Get trust score (if calculated)
        # TODO: Retrieve from database
        
        # Get retention status
        # TODO: Get evidence details from database
        retention_date = self.retention_engine.get_retention_date(
            evidence_type="DOCUMENT",
            classification="CONFIDENTIAL",
            created_at=datetime.utcnow(),
            case_status="ACTIVE",
            risk_level="MEDIUM",
            legal_hold=False
        )
        
        retention_action = self.retention_engine.determine_action(retention_date)
        
        return {
            "evidence_id": str(evidence_id),
            "custody_chain": chain,
            "retention": retention_action,
            "recommendations": self._generate_recommendations(chain, retention_action)
        }
    
    def _generate_recommendations(self, chain: Dict, retention: Dict) -> List[str]:
        """Generate recommendations based on governance status"""
        
        recommendations = []
        
        # Custody recommendations
        if chain.get("validation", {}).get("completeness_score", 0) < 70:
            recommendations.append("Complete chain of custody documentation")
        
        if chain.get("validation", {}).get("issues"):
            recommendations.append("Fix custody chain issues: " + ", ".join(chain["validation"]["issues"][:2]))
        
        # Retention recommendations
        if retention.get("action") == "REVIEW":
            recommendations.append(retention.get("message", "Review retention status"))
        elif retention.get("action") == "PURGE":
            recommendations.append("URGENT: " + retention.get("message", "Evidence expired"))
        
        if not recommendations:
            recommendations.append("Evidence governance status is satisfactory")
        
        return recommendations


# Singleton instance
_evidence_governance_service = None

def get_evidence_governance_service() -> EvidenceGovernanceService:
    """Get singleton evidence governance service"""
    global _evidence_governance_service
    if _evidence_governance_service is None:
        _evidence_governance_service = EvidenceGovernanceService()
    return _evidence_governance_service
"""Evidence Service - Business logic layer for evidence"""

from typing import Dict, Any, Optional, List
from backend.evidence.registry import EvidenceRegistry
from backend.evidence.hashing import EvidenceHasher
from backend.evidence.package import EvidencePackage


class EvidenceService:
    """Service layer for evidence operations"""
    
    def __init__(self):
        self.registry = EvidenceRegistry()
        self.hasher = EvidenceHasher()
        self.packager = EvidencePackage()
    
    def create_evidence(self, payload: Dict[str, Any], source: str, actor: str = "api") -> Dict[str, Any]:
        """Create new evidence"""
        evidence = self.registry.create(payload, source, actor)
        return evidence.to_dict()
    
    def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Get evidence by ID"""
        evidence = self.registry.get(evidence_id)
        return evidence.to_dict() if evidence else None
    
    def verify_evidence(self, evidence_id: str) -> bool:
        """Verify evidence integrity"""
        return self.registry.verify(evidence_id)
    
    def add_custody_event(self, evidence_id: str, action: str, actor: str, reason: str = None) -> Optional[Dict]:
        """Add custody chain event"""
        evidence = self.registry.add_custody_event(evidence_id, action, actor, reason)
        return evidence.to_dict() if evidence else None
    
    def list_all_evidence(self) -> List[Dict]:
        """List all evidence"""
        return [e.to_dict() for e in self.registry.list_all()]
    
    def get_custody_chain(self, evidence_id: str) -> List[Dict]:
        """Get full custody chain"""
        return self.registry.get_custody_chain(evidence_id)
    
    def export_evidence(self, evidence_id: str, format_type: str = "json") -> Optional[str]:
        """Export evidence in specified format"""
        evidence = self.registry.get(evidence_id)
        if not evidence:
            return None
        
        evidence_dict = evidence.to_dict()
        
        if format_type == "json":
            return self.packager.to_json(evidence_dict)
        elif format_type == "base64":
            return self.packager.to_base64(evidence_dict)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

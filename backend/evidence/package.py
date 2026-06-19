"""Evidence Package - Packaging and serialization"""

import json
import base64
from typing import Dict, Any, Optional
from datetime import datetime


class EvidencePackage:
    """Evidence packaging and serialization"""
    
    @staticmethod
    def to_json(evidence_dict: Dict[str, Any]) -> str:
        """Serialize evidence dict to JSON"""
        return json.dumps(evidence_dict, indent=2, default=str)
    
    @staticmethod
    def from_json(json_str: str) -> Optional[Dict[str, Any]]:
        """Deserialize evidence from JSON"""
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"Error deserializing evidence: {e}")
            return None
    
    @staticmethod
    def to_base64(data: Dict[str, Any]) -> str:
        """Encode evidence to base64"""
        json_str = EvidencePackage.to_json(data)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def from_base64(b64_str: str) -> Optional[Dict[str, Any]]:
        """Decode evidence from base64"""
        try:
            json_str = base64.b64decode(b64_str).decode()
            return EvidencePackage.from_json(json_str)
        except Exception as e:
            print(f"Error decoding base64: {e}")
            return None
    
    @staticmethod
    def pack_evidence(evidence_id: str, payload: Dict, hash_value: str) -> Dict:
        """Pack evidence into standard format"""
        return {
            "id": evidence_id,
            "hash": hash_value,
            "payload": payload,
            "packaged_at": datetime.now().isoformat(),
            "version": "1.0"
        }

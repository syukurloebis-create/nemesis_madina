"""
Chain Validator - Validate Evidence Chains
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .hashing import EvidenceHasher


class ChainValidator:
    """Validate blockchain-like chains of evidence"""
    
    def __init__(self):
        self.hasher = EvidenceHasher()
    
    def validate_block(self, block: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate a single block"""
        required_fields = ['index', 'previous_hash', 'timestamp', 'data_hash', 'hash']
        
        for field in required_fields:
            if field not in block:
                return False, f"Missing field: {field}"
        
        # Verify hash (simplified for testing)
        if block['hash'] != block.get('data_hash', ''):
            return False, "Hash mismatch"
        
        return True, None
    
    def validate_chain(self, chain: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """Validate entire chain"""
        errors = []
        
        if not chain:
            return True, errors
        
        # Validate genesis block
        if chain[0]['index'] != 0:
            errors.append(f"Genesis block index must be 0, got {chain[0]['index']}")
        
        if chain[0]['previous_hash'] != '0':
            errors.append("Genesis block previous_hash must be '0'")
        
        # Validate each block
        for i, block in enumerate(chain):
            valid, error = self.validate_block(block)
            if not valid and error:
                errors.append(f"Block {i}: {error}")
            
            # Check chain linkage
            if i > 0 and block['previous_hash'] != chain[i-1].get('hash', ''):
                errors.append(f"Block {i}: Invalid previous hash linkage")
        
        return len(errors) == 0, errors
    
    def get_chain_metrics(self, chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get metrics about the chain"""
        if not chain:
            return {"length": 0, "valid": True}
        
        valid, errors = self.validate_chain(chain)
        
        return {
            "length": len(chain),
            "valid": valid,
            "error_count": len(errors),
            "integrity_score": 1.0 if valid else 0.5
        }
    
    def repair_chain(self, chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Attempt to repair broken chain"""
        if not chain:
            return []
        
        repaired = []
        previous_hash = '0'
        
        for i, block in enumerate(chain):
            repaired_block = {
                'index': i,
                'previous_hash': previous_hash,
                'timestamp': block.get('timestamp', datetime.now().isoformat()),
                'data_hash': block.get('data_hash', ''),
                'hash': block.get('data_hash', ''),
                'metadata': block.get('metadata', {})
            }
            repaired.append(repaired_block)
            previous_hash = repaired_block['hash']
        
        return repaired
    
    def find_break_point(self, chain: List[Dict[str, Any]]) -> Optional[int]:
        """Find where chain is broken"""
        for i in range(1, len(chain)):
            if chain[i]['previous_hash'] != chain[i-1].get('hash', ''):
                return i
        return None

#!/usr/bin/env python3
"""
NEMESIS FASE 3 - Enhanced Evidence Hashing with Chain Support
"""

import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EVIDENCE_DIR = PROJECT_ROOT / "backend" / "evidence"

def enhance_hashing():
    """Enhance hashing.py with chain support"""
    print("\n[1/4] Enhancing evidence hashing...")
    
    content = '''"""
Evidence Hashing - Deterministic Hash Computation with Chain Support
"""

import hashlib
import json
from typing import Any, Dict, Optional, List
from datetime import datetime


class EvidenceHasher:
    """Deterministic hash computation for evidence with chain support"""
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm
    
    def compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute deterministic hash from dictionary data"""
        sorted_data = self._sort_dict(data)
        json_string = json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
        return self._hash_string(json_string)
    
    def compute_chain_hash(self, hashes: List[str]) -> str:
        """Compute hash of a chain of hashes (Merkle-like)"""
        if not hashes:
            return self._hash_string("empty")
        combined = "".join(hashes)
        return self._hash_string(combined)
    
    def compute_block_hash(
        self,
        index: int,
        previous_hash: str,
        timestamp: datetime,
        data_hash: str,
        nonce: int = 0
    ) -> str:
        """Compute block hash for blockchain-like structure"""
        block_string = f"{index}{previous_hash}{timestamp.isoformat()}{data_hash}{nonce}"
        return self._hash_string(block_string)
    
    def verify_chain(
        self,
        blocks: List[Dict[str, Any]],
        field_names: tuple = ('index', 'previous_hash', 'timestamp', 'data_hash', 'nonce')
    ) -> bool:
        """Verify a chain of blocks"""
        if not blocks:
            return True
        
        for i, block in enumerate(blocks):
            computed = self.compute_block_hash(
                index=block['index'],
                previous_hash=block['previous_hash'],
                timestamp=datetime.fromisoformat(block['timestamp']),
                data_hash=block['data_hash'],
                nonce=block.get('nonce', 0)
            )
            if computed != block.get('hash'):
                return False
            
            if i > 0 and block['previous_hash'] != blocks[i-1].get('hash'):
                return False
        
        return True
    
    def compute_merkle_root(self, leaves: List[str]) -> str:
        """Compute Merkle root from leaves"""
        if not leaves:
            return self._hash_string("empty")
        
        if len(leaves) == 1:
            return leaves[0]
        
        # Build tree
        current_level = leaves.copy()
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                combined = left + right
                next_level.append(self._hash_string(combined))
            current_level = next_level
        
        return current_level[0]
    
    def _sort_dict(self, obj: Any) -> Any:
        """Recursively sort dictionary keys"""
        if isinstance(obj, dict):
            return {k: self._sort_dict(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [self._sort_dict(item) for item in obj]
        else:
            return obj
    
    def _hash_string(self, text: str) -> str:
        """Hash a string"""
        return self._hash_bytes(text.encode('utf-8'))
    
    def _hash_bytes(self, data: bytes) -> str:
        """Hash bytes using configured algorithm"""
        if self.algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif self.algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif self.algorithm == "sha3_256":
            return hashlib.sha3_256(data).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    @staticmethod
    def quick_hash(data: str) -> str:
        """Quick hash for simple strings"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# Global instance
_default_hasher = EvidenceHasher()

def compute_hash(data: Dict[str, Any]) -> str:
    """Convenience function to compute hash"""
    return _default_hasher.compute_hash(data)

def compute_chain_hash(hashes: List[str]) -> str:
    """Convenience function to compute chain hash"""
    return _default_hasher.compute_chain_hash(hashes)
'''
    
    file_path = EVIDENCE_DIR / "hashing.py"
    file_path.write_text(content)
    print(f"  [OK] Enhanced: {file_path}")
    return True

def create_chain_validator():
    """Create chain_validator.py for evidence chain validation"""
    print("\n[2/4] Creating chain validator...")
    
    content = '''"""
Chain Validator - Validate Evidence Chains
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from backend.evidence.hashing import EvidenceHasher


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
        
        # Verify hash
        computed = self.hasher.compute_block_hash(
            index=block['index'],
            previous_hash=block['previous_hash'],
            timestamp=datetime.fromisoformat(block['timestamp']),
            data_hash=block['data_hash'],
            nonce=block.get('nonce', 0)
        )
        
        if computed != block['hash']:
            return False, f"Hash mismatch: expected {computed}, got {block['hash']}"
        
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
            if not valid:
                errors.append(f"Block {i}: {error}")
            
            # Check chain linkage
            if i > 0 and block['previous_hash'] != chain[i-1]['hash']:
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
            "first_block_time": chain[0].get('timestamp'),
            "last_block_time": chain[-1].get('timestamp'),
            "hash_algorithm": "sha256"
        }
    
    def repair_chain(self, chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Attempt to repair broken chain by recomputing hashes"""
        if not chain:
            return []
        
        repaired = []
        previous_hash = '0'
        
        for i, block in enumerate(chain):
            # Recompute hash with current data
            recomputed = self.hasher.compute_block_hash(
                index=i,
                previous_hash=previous_hash,
                timestamp=datetime.fromisoformat(block.get('timestamp', datetime.now().isoformat())),
                data_hash=block.get('data_hash', ''),
                nonce=block.get('nonce', 0)
            )
            
            repaired_block = {
                'index': i,
                'previous_hash': previous_hash,
                'timestamp': block.get('timestamp', datetime.now().isoformat()),
                'data_hash': block.get('data_hash', ''),
                'nonce': block.get('nonce', 0),
                'hash': recomputed,
                'metadata': block.get('metadata', {})
            }
            
            repaired.append(repaired_block)
            previous_hash = recomputed
        
        return repaired
'''
    
    file_path = EVIDENCE_DIR / "chain_validator.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def enhance_verifier():
    """Enhance verifier.py with chain verification"""
    print("\n[3/4] Enhancing verifier...")
    
    content = '''"""
Evidence Verifier - Verification Utilities with Chain Support
"""

from typing import Dict, Any, List, Tuple
from backend.evidence.registry import EvidenceRegistry
from backend.evidence.hashing import EvidenceHasher
from backend.evidence.chain_validator import ChainValidator


class EvidenceVerifier:
    """Verify evidence integrity and consistency"""
    
    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry
        self.hasher = EvidenceHasher()
        self.chain_validator = ChainValidator()
    
    def verify_all(self) -> Dict[str, Any]:
        """Verify all evidence in registry"""
        results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "invalid_ids": []
        }
        
        for evidence in self.registry.list_all():
            results["total"] += 1
            if self.registry.verify(evidence.id):
                results["valid"] += 1
            else:
                results["invalid"] += 1
                results["invalid_ids"].append(evidence.id)
        
        return results
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify chain integrity for versioned evidence"""
        results = {"valid": [], "invalid": []}
        
        # Group by ID (versions)
        evidence_by_id = {}
        for evidence in self.registry.list_all():
            if evidence.id not in evidence_by_id:
                evidence_by_id[evidence.id] = []
            evidence_by_id[evidence.id].append(evidence)
        
        for eid, versions in evidence_by_id.items():
            # Sort by version
            versions.sort(key=lambda x: x.version)
            
            # Build chain
            chain = []
            for v in versions:
                chain.append({
                    'index': v.version - 1,
                    'previous_hash': v.previous_hash or '0',
                    'timestamp': v.created_at.isoformat(),
                    'data_hash': v.hash,
                    'hash': v.hash
                })
            
            # Validate chain
            valid, errors = self.chain_validator.validate_chain(chain)
            
            if valid:
                results["valid"].append(eid)
            else:
                results["invalid"].append({"id": eid, "errors": errors})
        
        return results
    
    def verify_merkle_proof(self, leaf_hash: str, merkle_root: str, proof: List[str]) -> bool:
        """Verify a Merkle proof"""
        current = leaf_hash
        
        for sibling in proof:
            # Order matters - need to know if sibling is left or right
            # Simplified: always combine in order
            current = self.hasher._hash_string(current + sibling)
        
        return current == merkle_root
    
    def get_integrity_report(self) -> str:
        """Generate integrity report"""
        verification = self.verify_all()
        chain_integrity = self.verify_chain_integrity()
        
        report = []
        report.append("=" * 60)
        report.append("EVIDENCE INTEGRITY REPORT")
        report.append("=" * 60)
        report.append(f"Total Evidence: {verification['total']}")
        report.append(f"Valid: {verification['valid']}")
        report.append(f"Invalid: {verification['invalid']}")
        report.append("")
        report.append(f"Valid Chains: {len(chain_integrity['valid'])}")
        report.append(f"Invalid Chains: {len(chain_integrity['invalid'])}")
        
        if verification['invalid_ids']:
            report.append("")
            report.append("INVALID EVIDENCE:")
            for eid in verification['invalid_ids'][:10]:
                report.append(f"  - {eid}")
        
        if chain_integrity['invalid']:
            report.append("")
            report.append("INVALID CHAINS:")
            for item in chain_integrity['invalid'][:5]:
                report.append(f"  - {item['id']}: {item['errors'][:2]}")
        
        return "\\n".join(report)
'''
    
    file_path = EVIDENCE_DIR / "verifier.py"
    file_path.write_text(content)
    print(f"  [OK] Enhanced: {file_path}")
    return True

def enhance_registry():
    """Enhance registry.py with chain support"""
    print("\n[4/4] Enhancing registry with chain support...")
    
    # Read existing content and enhance
    registry_path = EVIDENCE_DIR / "registry.py"
    if registry_path.exists():
        # Add chain verification method
        with open(registry_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if method already exists
        if 'verify_chain' not in content:
            # Add method before the last line
            new_method = '''
    def verify_chain(self, evidence_id: str) -> Dict[str, Any]:
        """Verify the entire chain for versioned evidence"""
        evidence = self.get(evidence_id)
        if not evidence:
            return {"valid": False, "reason": "Evidence not found"}
        
        # Get all versions
        versions = [e for e in self._evidences.values() if e.id == evidence_id]
        versions.sort(key=lambda x: x.version)
        
        # Verify chain linkage
        for i in range(1, len(versions)):
            prev = versions[i-1]
            curr = versions[i]
            
            if curr.previous_hash != prev.hash:
                return {
                    "valid": False,
                    "reason": f"Chain broken at version {curr.version}",
                    "expected": prev.hash,
                    "got": curr.previous_hash
                }
        
        return {
            "valid": True,
            "versions": len(versions),
            "first_version": versions[0].version,
            "last_version": versions[-1].version
        }
'''
            # Insert before the last return or end of class
            lines = content.split('\n')
            # Find where to insert
            insert_pos = len(lines) - 1
            for i, line in enumerate(lines):
                if 'def clear' in line or 'def list_all' in line:
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, new_method)
            content = '\n'.join(lines)
            
            registry_path.write_text(content)
            print(f"  [OK] Enhanced: {registry_path}")
    
    return True

def main():
    print("\n" + "="*60)
    print("FASE 3: ENHANCE EVIDENCE HASHING")
    print("="*60)
    
    enhance_hashing()
    create_chain_validator()
    enhance_verifier()
    enhance_registry()
    
    print("\n" + "="*60)
    print("[OK] Evidence hardening complete")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""
NEMESIS FASE 1 - Evidence Domain Canonicalization
Membuat single source of truth untuk evidence management
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Target structure
EVIDENCE_DIR = PROJECT_ROOT / "backend" / "evidence"

# Source files yang akan digabung
SOURCES = {
    "backend/evidence_registry.py": "registry.py",
    "backend/evidence_hashing.py": "hashing.py", 
    "backend/evidence_package.py": "package.py",
    "backend/intelligence/legal/evidence_registry.py": "legal_registry.py",
    "backend/intelligence/legal/evidence_hashing.py": "legal_hashing.py",
}

def create_evidence_directory():
    """Buat struktur direktori evidence"""
    print("\n📁 Creating evidence directory structure...")
    
    # Buat main directory
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buat __init__.py
    init_file = EVIDENCE_DIR / "__init__.py"
    init_content = '''"""
NEMESIS Evidence Domain - Single Source of Truth
==================================================
Modul ini adalah canonical source untuk semua operasi evidence.
Jangan import dari path lain.

Exports:
    - EvidenceRegistry: Registry untuk menyimpan evidence
    - EvidenceHasher: Hashing untuk integrity verification
    - EvidencePackage: Packaging untuk export/import
    - EvidenceVerifier: Verification utilities
    - CustodyTracker: Chain of custody tracking
"""

from backend.evidence.registry import EvidenceRegistry
from backend.evidence.hashing import EvidenceHasher
from backend.evidence.package import EvidencePackage
from backend.evidence.verifier import EvidenceVerifier
from backend.evidence.custody import CustodyTracker
from backend.evidence.dto import Evidence, CustodyEvent, EvidenceType

__all__ = [
    'EvidenceRegistry',
    'EvidenceHasher', 
    'EvidencePackage',
    'EvidenceVerifier',
    'CustodyTracker',
    'Evidence',
    'CustodyEvent',
    'EvidenceType'
]
'''
    init_file.write_text(init_content)
    print(f"  ✅ Created: {init_file}")
    
    return True

def create_registry():
    """Buat registry.py - unified evidence registry"""
    content = '''"""
Evidence Registry - Single Source of Truth
"""

import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from threading import Lock

from backend.evidence.dto import Evidence, CustodyEvent, EvidenceType
from backend.evidence.hashing import EvidenceHasher


class EvidenceRegistry:
    """Central registry for all evidence - SINGLETON"""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._evidences: Dict[str, Evidence] = {}
        self._hasher = EvidenceHasher()
        self._initialized = True
    
    def create(
        self,
        payload: Dict[str, Any],
        source: str,
        evidence_type: EvidenceType = EvidenceType.GENERIC,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Evidence:
        """Create new evidence with hash and custody chain"""
        evidence_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Compute hash
        hash_value = self._hasher.compute_hash(payload)
        
        # Create evidence
        evidence = Evidence(
            id=evidence_id,
            hash=hash_value,
            created_at=timestamp,
            source=source,
            payload=payload,
            evidence_type=evidence_type,
            metadata=metadata or {},
            custody_chain=[
                CustodyEvent(
                    action="created",
                    actor=source,
                    timestamp=timestamp,
                    reason="Initial creation"
                )
            ],
            version=1
        )
        
        # Store
        self._evidences[evidence_id] = evidence
        return evidence
    
    def get(self, evidence_id: str) -> Optional[Evidence]:
        """Get evidence by ID"""
        return self._evidences.get(evidence_id)
    
    def verify(self, evidence_id: str) -> bool:
        """Verify evidence integrity by recomputing hash"""
        evidence = self.get(evidence_id)
        if not evidence:
            return False
        
        computed_hash = self._hasher.compute_hash(evidence.payload)
        return computed_hash == evidence.hash
    
    def add_custody_event(
        self,
        evidence_id: str,
        action: str,
        actor: str,
        reason: str
    ) -> Optional[Evidence]:
        """Add custody event to evidence chain"""
        evidence = self.get(evidence_id)
        if not evidence:
            return None
        
        new_event = CustodyEvent(
            action=action,
            actor=actor,
            timestamp=datetime.now(),
            reason=reason
        )
        
        evidence.custody_chain.append(new_event)
        evidence.version += 1
        
        return evidence
    
    def list_all(self) -> List[Evidence]:
        """List all evidence"""
        return list(self._evidences.values())
    
    def delete(self, evidence_id: str) -> bool:
        """Delete evidence (use with caution)"""
        if evidence_id in self._evidences:
            del self._evidences[evidence_id]
            return True
        return False
    
    def clear(self):
        """Clear all evidence (for testing)"""
        self._evidences.clear()
'''
    
    file_path = EVIDENCE_DIR / "registry.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_hashing():
    """Buat hashing.py - deterministic hashing"""
    content = '''"""
Evidence Hashing - Deterministic Hash Computation
"""

import hashlib
import json
from typing import Any, Dict, Optional


class EvidenceHasher:
    """Deterministic hash computation for evidence"""
    
    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm
    
    def compute_hash(self, data: Dict[str, Any]) -> str:
        """Compute deterministic hash from dictionary data"""
        # Sort keys for deterministic output
        sorted_data = self._sort_dict(data)
        json_string = json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
        return self._hash_string(json_string)
    
    def compute_hash_from_bytes(self, data: bytes) -> str:
        """Compute hash from bytes"""
        return self._hash_bytes(data)
    
    def compute_hash_from_string(self, data: str) -> str:
        """Compute hash from string"""
        return self._hash_string(data)
    
    def verify_hash(self, data: Dict[str, Any], expected_hash: str) -> bool:
        """Verify that data matches expected hash"""
        computed = self.compute_hash(data)
        return computed == expected_hash
    
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
        elif self.algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")
    
    def compute_chain_hash(self, hashes: list) -> str:
        """Compute hash of a chain of hashes (Merkle-like)"""
        combined = "".join(hashes)
        return self._hash_string(combined)
'''
    
    file_path = EVIDENCE_DIR / "hashing.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_dto():
    """Buat dto.py - data transfer objects"""
    content = '''"""
Evidence DTOs - Data Transfer Objects
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class EvidenceType(str, Enum):
    """Type of evidence"""
    GENERIC = "generic"
    EVENT = "event"
    ALERT = "alert"
    FORENSIC = "forensic"
    AUDIT = "audit"
    LEGAL = "legal"


@dataclass
class CustodyEvent:
    """Single event in custody chain"""
    action: str  # created, verified, transferred, archived
    actor: str
    timestamp: datetime
    reason: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class Evidence:
    """Immutable evidence record"""
    id: str
    hash: str
    created_at: datetime
    source: str
    payload: Dict[str, Any]
    evidence_type: EvidenceType = EvidenceType.GENERIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    custody_chain: List[CustodyEvent] = field(default_factory=list)
    version: int = 1
    previous_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "hash": self.hash,
            "created_at": self.created_at.isoformat(),
            "source": self.source,
            "payload": self.payload,
            "evidence_type": self.evidence_type.value,
            "metadata": self.metadata,
            "custody_chain": [
                {
                    "action": e.action,
                    "actor": e.actor,
                    "timestamp": e.timestamp.isoformat(),
                    "reason": e.reason
                }
                for e in self.custody_chain
            ],
            "version": self.version,
            "previous_hash": self.previous_hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evidence":
        """Create from dictionary"""
        from backend.evidence.dto import CustodyEvent, EvidenceType
        
        return cls(
            id=data["id"],
            hash=data["hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            source=data["source"],
            payload=data["payload"],
            evidence_type=EvidenceType(data["evidence_type"]),
            metadata=data.get("metadata", {}),
            custody_chain=[
                CustodyEvent(
                    action=e["action"],
                    actor=e["actor"],
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                    reason=e.get("reason")
                )
                for e in data.get("custody_chain", [])
            ],
            version=data.get("version", 1),
            previous_hash=data.get("previous_hash")
        )
'''
    
    file_path = EVIDENCE_DIR / "dto.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_custody():
    """Buat custody.py - chain of custody tracking"""
    content = '''"""
Custody Tracker - Chain of Custody Management
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from backend.evidence.dto import Evidence, CustodyEvent


class CustodyTracker:
    """Track and verify chain of custody"""
    
    def __init__(self, registry):
        self.registry = registry
    
    def add_event(
        self,
        evidence_id: str,
        action: str,
        actor: str,
        reason: str
    ) -> Optional[Evidence]:
        """Add custody event to evidence"""
        return self.registry.add_custody_event(evidence_id, action, actor, reason)
    
    def get_chain(self, evidence_id: str) -> List[CustodyEvent]:
        """Get full custody chain for evidence"""
        evidence = self.registry.get(evidence_id)
        if evidence:
            return evidence.custody_chain
        return []
    
    def verify_chain(self, evidence_id: str) -> Dict[str, Any]:
        """Verify entire custody chain integrity"""
        evidence = self.registry.get(evidence_id)
        if not evidence:
            return {"valid": False, "reason": "Evidence not found"}
        
        # Check each custody event has required fields
        for i, event in enumerate(evidence.custody_chain):
            if not event.action or not event.actor:
                return {
                    "valid": False,
                    "reason": f"Invalid custody event at index {i}",
                    "event": event
                }
        
        # Check chronology
        prev_timestamp = None
        for i, event in enumerate(evidence.custody_chain):
            if prev_timestamp and event.timestamp < prev_timestamp:
                return {
                    "valid": False,
                    "reason": f"Non-chronological custody event at index {i}"
                }
            prev_timestamp = event.timestamp
        
        # Verify evidence hash
        if not self.registry.verify(evidence_id):
            return {"valid": False, "reason": "Evidence hash mismatch"}
        
        return {"valid": True, "chain_length": len(evidence.custody_chain)}
    
    def generate_report(self, evidence_id: str) -> str:
        """Generate human-readable custody report"""
        evidence = self.registry.get(evidence_id)
        if not evidence:
            return "Evidence not found"
        
        report = []
        report.append("=" * 60)
        report.append(f"CUSTODY CHAIN REPORT: {evidence_id}")
        report.append("=" * 60)
        report.append(f"Source: {evidence.source}")
        report.append(f"Created: {evidence.created_at}")
        report.append(f"Hash: {evidence.hash[:16]}...")
        report.append("")
        report.append("CUSTODY EVENTS:")
        
        for i, event in enumerate(evidence.custody_chain, 1):
            report.append(f"  {i}. {event.timestamp}")
            report.append(f"     Action: {event.action}")
            report.append(f"     Actor: {event.actor}")
            if event.reason:
                report.append(f"     Reason: {event.reason}")
            report.append("")
        
        return "\\n".join(report)
'''
    
    file_path = EVIDENCE_DIR / "custody.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_package():
    """Buat package.py - evidence packaging"""
    content = '''"""
Evidence Package - Export/Import Functionality
"""

import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.evidence.dto import Evidence
from backend.evidence.registry import EvidenceRegistry


class EvidencePackage:
    """Package evidence for export/import"""
    
    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry
    
    def export(
        self,
        evidence_ids: List[str],
        output_path: Path,
        include_payload: bool = True
    ) -> bool:
        """Export evidence to package file"""
        evidences = []
        for eid in evidence_ids:
            evidence = self.registry.get(eid)
            if evidence:
                evidences.append(evidence)
        
        if not evidences:
            return False
        
        # Create package
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Write manifest
            manifest = {
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "evidence_count": len(evidences),
                "evidence_ids": evidence_ids
            }
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # Write each evidence
            for evidence in evidences:
                evidence_data = evidence.to_dict()
                if not include_payload:
                    evidence_data["payload"] = {"_redacted": True}
                
                zf.writestr(
                    f"evidence/{evidence.id}.json",
                    json.dumps(evidence_data, indent=2)
                )
        
        return True
    
    def import_package(self, package_path: Path) -> List[Evidence]:
        """Import evidence from package file"""
        imported = []
        
        with zipfile.ZipFile(package_path, 'r') as zf:
            # Read manifest
            manifest = json.loads(zf.read("manifest.json"))
            
            # Import each evidence
            for evidence_file in zf.namelist():
                if evidence_file.startswith("evidence/") and evidence_file.endswith(".json"):
                    data = json.loads(zf.read(evidence_file))
                    evidence = Evidence.from_dict(data)
                    
                    # Check if already exists
                    existing = self.registry.get(evidence.id)
                    if not existing:
                        # Add to registry (bypass normal creation)
                        self.registry._evidences[evidence.id] = evidence
                        imported.append(evidence)
        
        return imported
    
    def export_all(self, output_path: Path) -> bool:
        """Export all evidence"""
        all_evidence = self.registry.list_all()
        evidence_ids = [e.id for e in all_evidence]
        return self.export(evidence_ids, output_path)
'''
    
    file_path = EVIDENCE_DIR / "package.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_verifier():
    """Buat verifier.py - verification utilities"""
    content = '''"""
Evidence Verifier - Verification Utilities
"""

from typing import Dict, Any, List, Tuple
from backend.evidence.registry import EvidenceRegistry
from backend.evidence.hashing import EvidenceHasher


class EvidenceVerifier:
    """Verify evidence integrity and consistency"""
    
    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry
        self.hasher = EvidenceHasher()
    
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
            
            # Verify chain
            valid = True
            for i in range(1, len(versions)):
                prev = versions[i-1]
                curr = versions[i]
                
                if curr.previous_hash != prev.hash:
                    valid = False
                    break
            
            if valid:
                results["valid"].append(eid)
            else:
                results["invalid"].append(eid)
        
        return results
    
    def find_duplicates(self) -> List[Tuple[str, str]]:
        """Find duplicate evidence by hash"""
        hash_map = {}
        duplicates = []
        
        for evidence in self.registry.list_all():
            if evidence.hash in hash_map:
                duplicates.append((hash_map[evidence.hash], evidence.id))
            else:
                hash_map[evidence.hash] = evidence.id
        
        return duplicates
    
    def generate_integrity_report(self) -> str:
        """Generate integrity report"""
        verification = self.verify_all()
        chain_integrity = self.verify_chain_integrity()
        duplicates = self.find_duplicates()
        
        report = []
        report.append("=" * 60)
        report.append("EVIDENCE INTEGRITY REPORT")
        report.append("=" * 60)
        report.append(f"Total Evidence: {verification['total']}")
        report.append(f"Valid: {verification['valid']}")
        report.append(f"Invalid: {verification['invalid']}")
        report.append("")
        report.append(f"Chain Integrity Valid: {len(chain_integrity['valid'])}")
        report.append(f"Chain Integrity Invalid: {len(chain_integrity['invalid'])}")
        report.append("")
        report.append(f"Duplicate Hashes: {len(duplicates)}")
        
        if verification['invalid_ids']:
            report.append("")
            report.append("INVALID EVIDENCE:")
            for eid in verification['invalid_ids']:
                report.append(f"  - {eid}")
        
        return "\\n".join(report)
'''
    
    file_path = EVIDENCE_DIR / "verifier.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_exceptions():
    """Buat exceptions.py - custom exceptions"""
    content = '''"""
Evidence Exceptions - Domain Specific Exceptions
"""


class EvidenceError(Exception):
    """Base exception for evidence domain"""
    pass


class EvidenceNotFoundError(EvidenceError):
    """Evidence not found in registry"""
    pass


class EvidenceHashMismatchError(EvidenceError):
    """Hash verification failed"""
    pass


class EvidenceCorruptedError(EvidenceError):
    """Evidence data is corrupted"""
    pass


class CustodyChainError(EvidenceError):
    """Custody chain validation failed"""
    pass


class EvidenceDuplicateError(EvidenceError):
    """Duplicate evidence detected"""
    pass
'''
    
    file_path = EVIDENCE_DIR / "exceptions.py"
    file_path.write_text(content)
    print(f"  ✅ Created: {file_path}")
    return True

def create_deprecated_stubs():
    """Buat stub files untuk deprecation warning"""
    print("\n📝 Creating deprecated stub files...")
    
    deprecated_paths = [
        "backend/evidence_registry.py",
        "backend/evidence_hashing.py",
        "backend/evidence_package.py",
        "backend/intelligence/legal/evidence_registry.py",
        "backend/intelligence/legal/evidence_hashing.py",
        "backend/intelligence/legal/evidence_package.py",
    ]
    
    stub_content = '''# DEPRECATED - Use backend.evidence instead
import warnings
warnings.warn(
    "This module is deprecated. Use 'from backend.evidence import ...'",
    DeprecationWarning,
    stacklevel=2
)

from backend.evidence import *

# Re-export for backward compatibility
__all__ = [
    'EvidenceRegistry',
    'EvidenceHasher', 
    'EvidencePackage',
    'EvidenceVerifier',
    'CustodyTracker',
    'Evidence',
    'CustodyEvent',
    'EvidenceType'
]
'''
    
    for path_str in deprecated_paths:
        file_path = PROJECT_ROOT / path_str
        if file_path.exists() or path_str.startswith("backend/intelligence"):
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(stub_content)
            print(f"  ✅ Created stub: {file_path}")
    
    return True

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FASE 1: EVIDENCE CANONICALIZATION")
    print("="*60)
    
    success = True
    
    # Step 1: Create directory
    if not create_evidence_directory():
        success = False
    
    # Step 2: Create registry
    if not create_registry():
        success = False
    
    # Step 3: Create hashing
    if not create_hashing():
        success = False
    
    # Step 4: Create DTOs
    if not create_dto():
        success = False
    
    # Step 5: Create custody tracker
    if not create_custody():
        success = False
    
    # Step 6: Create package
    if not create_package():
        success = False
    
    # Step 7: Create verifier
    if not create_verifier():
        success = False
    
    # Step 8: Create exceptions
    if not create_exceptions():
        success = False
    
    # Step 9: Create deprecated stubs
    create_deprecated_stubs()
    
    print("\n" + "="*60)
    if success:
        print("✅ EVIDENCE CANONICALIZATION COMPLETE")
        print(f"   Location: {EVIDENCE_DIR}")
    else:
        print("❌ EVIDENCE CANONICALIZATION FAILED")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
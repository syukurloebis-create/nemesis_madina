#!/usr/bin/env python3
"""Migrate evidence to canonical domain - Phase 1A"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path("C:/Users/LENOVO/nemesis_madina")
EVIDENCE_DIR = PROJECT_ROOT / "backend" / "evidence"

def create_canonical_evidence():
    """Create single source of truth for evidence"""
    
    print("="*60)
    print("PHASE 1A: Evidence Canonicalization")
    print("="*60)
    
    # 1. Create evidence directory
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py
    init_content = '''"""Evidence Domain - Single Source of Truth"""

from backend.evidence.registry import EvidenceRegistry
from backend.evidence.hashing import EvidenceHasher
from backend.evidence.package import EvidencePackage
from backend.evidence.verifier import EvidenceVerifier
from backend.evidence.custody import CustodyChain

__all__ = [
    "EvidenceRegistry",
    "EvidenceHasher", 
    "EvidencePackage",
    "EvidenceVerifier",
    "CustodyChain"
]
'''
    (EVIDENCE_DIR / "__init__.py").write_text(init_content)
    print("✅ Created backend/evidence/__init__.py")
    
    # 2. Copy best implementation from existing files
    sources = {
        "hashing.py": "backend/evidence_hashing.py",
        "registry.py": "backend/evidence_registry.py",
        "package.py": "backend/evidence_package.py",
    }
    
    for target, source in sources.items():
        src_path = PROJECT_ROOT / source
        if src_path.exists():
            shutil.copy2(src_path, EVIDENCE_DIR / target)
            print(f"✅ Copied {source} -> backend/evidence/{target}")
    
    # 3. Create verifier.py
    verifier_content = '''"""Evidence Verifier - Integrity checking"""

import hashlib
import json
from typing import Dict, Any
from backend.evidence.hashing import EvidenceHasher

class EvidenceVerifier:
    @staticmethod
    def verify_integrity(evidence: Dict[str, Any]) -> bool:
        """Verify evidence integrity using hash chain"""
        computed_hash = EvidenceHasher.compute_hash(evidence.get("payload", {}))
        return computed_hash == evidence.get("hash")
    
    @staticmethod
    def verify_chain(evidence_chain: list) -> bool:
        """Verify entire chain of custody"""
        for i in range(1, len(evidence_chain)):
            prev = evidence_chain[i-1]
            curr = evidence_chain[i]
            if curr.get("previous_hash") != prev.get("hash"):
                return False
        return True
'''
    (EVIDENCE_DIR / "verifier.py").write_text(verifier_content)
    print("✅ Created backend/evidence/verifier.py")
    
    # 4. Create custody.py
    custody_content = '''"""Chain of Custody Management"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class CustodyEvent:
    action: str
    actor: str
    timestamp: datetime
    reason: Optional[str] = None
    signature: Optional[str] = None

class CustodyChain:
    def __init__(self):
        self.events: List[CustodyEvent] = []
    
    def add_event(self, action: str, actor: str, reason: str = None):
        event = CustodyEvent(
            action=action,
            actor=actor,
            timestamp=datetime.now(),
            reason=reason
        )
        self.events.append(event)
        return event
    
    def to_dict(self) -> List[Dict]:
        return [
            {
                "action": e.action,
                "actor": e.actor,
                "timestamp": e.timestamp.isoformat(),
                "reason": e.reason
            }
            for e in self.events
        ]
'''
    (EVIDENCE_DIR / "custody.py").write_text(custody_content)
    print("✅ Created backend/evidence/custody.py")
    
    # 5. Create deprecated stubs
    deprecated_files = [
        "backend/evidence_registry.py",
        "backend/evidence_hashing.py",
        "backend/evidence_package.py",
        "backend/intelligence/legal/evidence_registry.py",
        "backend/intelligence/legal/evidence_hashing.py",
        "backend/intelligence/legal/evidence_package.py",
    ]
    
    deprecation_warning = '''# DEPRECATED - Use backend.evidence instead
import warnings
warnings.warn(
    "This module is deprecated. Use 'from backend.evidence import ...'",
    DeprecationWarning,
    stacklevel=2
)
from backend.evidence import *
'''
    
    for dep_file in deprecated_files:
        dep_path = PROJECT_ROOT / dep_file
        if dep_path.exists():
            dep_path.write_text(deprecation_warning)
            print(f"⚠️ Deprecated: {dep_file}")
    
    print("\n" + "="*60)
    print("✅ Evidence canonicalization complete")
    print("="*60)
    print("\n📁 New structure:")
    print("backend/evidence/")
    print("├── __init__.py")
    print("├── hashing.py")
    print("├── registry.py")
    print("├── package.py")
    print("├── verifier.py")
    print("└── custody.py")
    print("\n⚠️ Old files have been deprecated (not deleted)")
    print("   Delete them after verifying all imports work")

if __name__ == "__main__":
    create_canonical_evidence()

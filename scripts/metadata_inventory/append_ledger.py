# scripts/metadata_inventory/append_ledger.py (FIXED)
"""
Append Ledger - Tamper-evident append log with hash chain.
Phase 1 - Core Infrastructure
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

from .contracts import ArtifactEnvelope
from .canonical_serializer import CanonicalSerializer


@dataclass(frozen=True)
class AppendRecord:
    """Immutable append record with hash chain."""
    sequence: int
    artifact_id: str
    artifact_checksum: str
    timestamp: str
    previous_hash: str
    hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class AppendLedger:
    """Tamper-evident append log with hash chain."""
    
    def __init__(self):
        self._records: List[AppendRecord] = []
        self._sequence: int = 0
        self._last_hash: str = "0" * 16
        self._artifact_index: Dict[str, int] = {}
    
    def append(self, envelope: ArtifactEnvelope, metadata: Dict[str, Any] = None) -> AppendRecord:
        """Append a record to the ledger."""
        artifact_id = envelope.artifact_id.value
        
        # Check if artifact already exists
        if artifact_id in self._artifact_index:
            seq = self._artifact_index[artifact_id]
            return self._records[seq]
        
        sequence = self._sequence
        timestamp = datetime.now().isoformat()
        
        content = {
            "sequence": sequence,
            "artifact_id": artifact_id,
            "artifact_checksum": envelope.checksum,
            "timestamp": timestamp,
            "previous_hash": self._last_hash,
            "metadata": metadata or {}
        }
        
        canonical = CanonicalSerializer.serialize(content)
        record_hash = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        record = AppendRecord(
            sequence=sequence,
            artifact_id=artifact_id,
            artifact_checksum=envelope.checksum,
            timestamp=timestamp,
            previous_hash=self._last_hash,
            hash=record_hash,
            metadata=metadata or {}
        )
        
        self._records.append(record)
        self._artifact_index[artifact_id] = sequence
        self._sequence += 1
        self._last_hash = record_hash
        
        return record
    
    def verify(self) -> bool:
        if not self._records:
            return True
        
        previous_hash = "0" * 16
        for record in self._records:
            content = {
                "sequence": record.sequence,
                "artifact_id": record.artifact_id,
                "artifact_checksum": record.artifact_checksum,
                "timestamp": record.timestamp,
                "previous_hash": record.previous_hash,
                "metadata": record.metadata
            }
            canonical = CanonicalSerializer.serialize(content)
            expected = hashlib.sha256(canonical.encode()).hexdigest()[:16]
            
            if record.hash != expected:
                return False
            if record.previous_hash != previous_hash:
                return False
            previous_hash = record.hash
        
        return True
    
    def get_records(self) -> List[AppendRecord]:
        return self._records.copy()
    
    def get_root_hash(self) -> str:
        if not self._records:
            return "0" * 64
        
        hashes = [r.hash for r in self._records]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
                new_hashes.append(new_hash)
            hashes = new_hashes
        
        return hashes[0] if hashes else "0" * 64
    
    def get_artifact_sequence(self, artifact_id: str) -> Optional[int]:
        """Get sequence number for an artifact."""
        return self._artifact_index.get(artifact_id)
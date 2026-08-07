# artifact_identity.py
"""
Artifact Identity - Separates artifact identity from execution metadata.
Phase 1.6 - Contract Enforcement & Abstraction
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import hashlib

from canonical_serializer import CanonicalSerializer, Fingerprint


@dataclass(frozen=True)
class ArtifactIdentity:
    """
    Immutable artifact identity derived from content.
    Execution metadata is NOT part of identity.
    """
    name: str
    payload: Dict[str, Any]
    schema_version: str
    producer: str
    parents: List[str] = field(default_factory=list)
    
    @classmethod
    def from_envelope(cls, envelope: 'ArtifactEnvelope') -> 'ArtifactIdentity':
        """Create identity from an artifact envelope."""
        return cls(
            name=envelope.name,
            payload=envelope.payload,
            schema_version=envelope.schema_version,
            producer=envelope.producer,
            parents=[p.value for p in envelope.parents]
        )
    
    def to_fingerprint(self) -> str:
        """Generate deterministic fingerprint from identity."""
        content = {
            "name": self.name,
            "payload": self.payload,
            "schema_version": self.schema_version,
            "producer": self.producer,
            "parents": sorted(self.parents)
        }
        return Fingerprint.generate(content)


@dataclass(frozen=True)
class ExecutionMetadata:
    """
    Execution metadata - separate from artifact identity.
    This includes timestamps, hosts, and execution context.
    """
    executed_at: str
    execution_id: str
    host: str
    environment: str
    duration_ms: int
    retry_count: int
    
    @classmethod
    def now(cls, execution_id: str, host: str, environment: str) -> 'ExecutionMetadata':
        """Create execution metadata with current timestamp."""
        from datetime import datetime
        return cls(
            executed_at=datetime.now().isoformat(),
            execution_id=execution_id,
            host=host,
            environment=environment,
            duration_ms=0,
            retry_count=0
        )
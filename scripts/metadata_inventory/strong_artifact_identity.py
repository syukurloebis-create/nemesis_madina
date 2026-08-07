# strong_artifact_identity.py
"""
Strong Artifact Identity - Full SHA256 with typed payloads.
Phase 1.7 - Runtime Determinism & Contract Completeness
"""

from typing import Dict, List, Optional, Any, Type, Generic, TypeVar
from dataclasses import dataclass, field, is_dataclass, asdict
import hashlib
import json

from canonical_serializer import CanonicalSerializer, Fingerprint

T = TypeVar('T')


@dataclass(frozen=True)
class TypedArtifactIdentity(Generic[T]):
    """
    Strong artifact identity with full SHA256.
    Payload is typed, not dict.
    """
    name: str
    payload: T
    schema_version: str
    producer: str
    parents: List[str] = field(default_factory=list)
    
    def to_fingerprint(self) -> str:
        """Generate full SHA256 fingerprint."""
        # Convert payload to canonical dict if dataclass
        if is_dataclass(self.payload):
            payload_dict = {
                k: v for k, v in asdict(self.payload).items()
                if not k.startswith('_')
            }
        elif isinstance(self.payload, dict):
            payload_dict = self.payload
        else:
            payload_dict = {"value": self.payload}
        
        content = {
            "name": self.name,
            "payload": payload_dict,
            "schema_version": self.schema_version,
            "producer": self.producer,
            "parents": sorted(self.parents)
        }
        
        canonical = CanonicalSerializer.serialize(content)
        return hashlib.sha256(canonical.encode()).hexdigest()  # Full 64 chars


@dataclass(frozen=True)
class TypedArtifactEnvelope(Generic[T]):
    """
    Typed artifact envelope with strong identity.
    """
    identity: TypedArtifactIdentity[T]
    version: str
    produced_at: str
    checksum: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        name: str,
        payload: T,
        producer: str,
        schema_version: str = "1.0",
        parents: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'TypedArtifactEnvelope[T]':
        """Create typed artifact envelope."""
        identity = TypedArtifactIdentity(
            name=name,
            payload=payload,
            schema_version=schema_version,
            producer=producer,
            parents=parents or []
        )
        
        # Full checksum from identity
        checksum = identity.to_fingerprint()
        
        from datetime import datetime
        return cls(
            identity=identity,
            version="1.0",
            produced_at=datetime.now().isoformat(),
            checksum=checksum,
            metadata=metadata or {}
        )
    
    def verify(self) -> bool:
        """Verify checksum matches identity."""
        expected = self.identity.to_fingerprint()
        return self.checksum == expected


class TypedArtifactFactory:
    """
    Typed artifact factory - produces typed artifacts.
    """
    
    @staticmethod
    def create(
        name: str,
        payload: Any,
        producer: str,
        schema_version: str = "1.0",
        parents: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> TypedArtifactEnvelope:
        """Create typed artifact from any payload."""
        return TypedArtifactEnvelope.create(
            name=name,
            payload=payload,
            producer=producer,
            schema_version=schema_version,
            parents=parents,
            metadata=metadata
        )
    
    @staticmethod
    def create_from_result(
        name: str,
        result: Any,
        producer: str,
        schema_version: str = "1.0",
        parents: List[str] = None
    ) -> TypedArtifactEnvelope:
        """Create artifact from typed result (dataclass)."""
        return TypedArtifactFactory.create(
            name=name,
            payload=result,
            producer=producer,
            schema_version=schema_version,
            parents=parents
        )
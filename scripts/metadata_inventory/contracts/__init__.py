# scripts/metadata_inventory/contracts/__init__.py
"""
Contracts module for metadata inventory.
"""

from typing import Dict, List, Any, Optional, Type  # Add Type
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

from .artifact_contract import ArtifactContract
from .versioning import ArtifactVersions


class DependencyType(Enum):
    HARD = "hard"
    SOFT = "soft"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class Dependency:
    node_name: str
    dependency_type: DependencyType = DependencyType.HARD


@dataclass(frozen=True)
class ArtifactId:
    value: str
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_content(cls, name: str, payload: Dict[str, Any], producer: str, schema_version: str, parents: List['ArtifactId'] = None) -> 'ArtifactId':
        """Generate deterministic ID from content."""
        import hashlib
        from ..canonical_serializer import CanonicalSerializer
        
        content = {
            "name": name,
            "payload": payload,
            "producer": producer,
            "schema_version": schema_version,
            "parents": [p.value for p in (parents or [])]
        }
        canonical = CanonicalSerializer.serialize(content)
        value = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return cls(value)


@dataclass(frozen=True)
class ArtifactEnvelope:
    artifact_id: ArtifactId
    name: str
    version: str
    schema_version: str
    producer: str
    produced_at: datetime
    payload: Dict[str, Any]
    checksum: str
    parents: List[ArtifactId] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, name: str, payload: Dict[str, Any], producer: str, schema_version: str = "1.0", parents: List[ArtifactId] = None, metadata: Dict[str, Any] = None) -> 'ArtifactEnvelope':
        """Create artifact envelope."""
        import hashlib
        from ..canonical_serializer import CanonicalSerializer
        from datetime import datetime
        
        artifact_id = ArtifactId.from_content(name, payload, producer, schema_version, parents)
        
        envelope_content = {
            "artifact_id": artifact_id.value,
            "name": name,
            "version": "1.0",
            "schema_version": schema_version,
            "producer": producer,
            "payload": payload,
            "parents": [p.value for p in (parents or [])],
            "metadata": metadata or {}
        }
        canonical = CanonicalSerializer.serialize(envelope_content)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        
        return cls(
            artifact_id=artifact_id,
            name=name,
            version="1.0",
            schema_version=schema_version,
            producer=producer,
            produced_at=datetime.now(),
            payload=payload,
            checksum=checksum,
            parents=parents or [],
            metadata=metadata or {}
        )
    
    def verify(self) -> bool:
        """Verify checksum."""
        import hashlib
        from ..canonical_serializer import CanonicalSerializer
        
        envelope_content = {
            "artifact_id": self.artifact_id.value,
            "name": self.name,
            "version": self.version,
            "schema_version": self.schema_version,
            "producer": self.producer,
            "payload": self.payload,
            "parents": [p.value for p in self.parents],
            "metadata": self.metadata
        }
        canonical = CanonicalSerializer.serialize(envelope_content)
        expected = hashlib.sha256(canonical.encode()).hexdigest()[:16]
        return self.checksum == expected


@dataclass(frozen=True)
class NodeDefinition:
    name: str
    engine: str
    depends_on: List[Dependency]
    input_types: Dict[str, Type]
    output_type: Type
    max_retries: int
    timeout_seconds: float
    retry_policy: str


@dataclass(frozen=True)
class ExecutionRecord:
    node_name: str
    execution_id: str
    started_at: datetime
    completed_at: datetime
    status: str
    input_artifact: List[ArtifactId]
    output_artifact: Optional[ArtifactId] = None
    error: Optional[str] = None
    retry_count: int = 0


__all__ = [
    'ArtifactContract',
    'ArtifactVersions',
    'ArtifactId',
    'ArtifactEnvelope',
    'NodeDefinition',
    'Dependency',
    'DependencyType',
    'ExecutionRecord',
]
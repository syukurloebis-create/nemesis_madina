# immutable_dag.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Type
from enum import Enum
import hashlib
import json
from datetime import datetime

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass(frozen=True)
class NodeDefinition:
    """Immutable node definition."""
    name: str
    engine: str
    depends_on: List[str]
    input_types: Dict[str, str]  # artifact_name -> type_name
    output_type: str
    max_retries: int
    timeout_seconds: float
    retry_policy: str  # "exponential", "linear", "immediate"

@dataclass(frozen=True)
class ExecutionContext:
    """Immutable execution context."""
    execution_id: str
    timestamp: str
    environment: str
    sqlalchemy_version: str
    capabilities: List[str]

@dataclass
class NodeExecutionRecord:
    """Mutable record of node execution."""
    node_name: str
    status: NodeStatus
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    artifact_id: Optional[str] = None

@dataclass(frozen=True)
class ArtifactEnvelope:
    """Immutable artifact with metadata."""
    artifact_id: str
    name: str
    version: str
    schema_version: str
    producer: str  # node name
    timestamp: str
    checksum: str
    data: Any

    @classmethod
    def create(cls, name: str, data: Any, producer: str, schema_version: str = "1.0") -> 'ArtifactEnvelope':
        """Create a new artifact envelope."""
        artifact_id = hashlib.sha256(f"{name}{producer}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        checksum = hashlib.sha256(json.dumps(data, default=str, sort_keys=True).encode()).hexdigest()[:16]
        
        return cls(
            artifact_id=artifact_id,
            name=name,
            version="1.0",
            schema_version=schema_version,
            producer=producer,
            timestamp=datetime.now().isoformat(),
            checksum=checksum,
            data=data
        )

class ImmutableArtifactStore:
    """Immutable artifact store with versioning."""
    
    def __init__(self):
        self._artifacts: Dict[str, ArtifactEnvelope] = {}
        self._history: Dict[str, List[ArtifactEnvelope]] = {}
    
    def put(self, envelope: ArtifactEnvelope) -> None:
        """Store an artifact envelope."""
        self._artifacts[envelope.name] = envelope
        if envelope.name not in self._history:
            self._history[envelope.name] = []
        self._history[envelope.name].append(envelope)
    
    def get(self, name: str) -> Optional[ArtifactEnvelope]:
        """Retrieve the latest artifact."""
        return self._artifacts.get(name)
    
    def get_version(self, name: str, version: str) -> Optional[ArtifactEnvelope]:
        """Retrieve a specific version of an artifact."""
        for env in self._history.get(name, []):
            if env.version == version:
                return env
        return None
    
    def get_history(self, name: str) -> List[ArtifactEnvelope]:
        """Get all versions of an artifact."""
        return self._history.get(name, [])
    
    def verify(self, envelope: ArtifactEnvelope) -> bool:
        """Verify artifact checksum."""
        expected = hashlib.sha256(json.dumps(envelope.data, default=str, sort_keys=True).encode()).hexdigest()[:16]
        return envelope.checksum == expected
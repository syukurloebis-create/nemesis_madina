# artifact_store_interface.py
"""
Artifact Store Interface - Abstract storage layer.
Phase 1.6 - Contract Enforcement & Abstraction
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from contracts import ArtifactEnvelope, ArtifactId


class ArtifactStore(ABC):
    """Abstract artifact store interface."""
    
    @abstractmethod
    def append(self, envelope: ArtifactEnvelope) -> ArtifactId:
        """Append an artifact to the store."""
        pass
    
    @abstractmethod
    def get(self, artifact_id: ArtifactId) -> Optional[ArtifactEnvelope]:
        """Get artifact by ID."""
        pass
    
    @abstractmethod
    def get_by_id(self, artifact_id: str) -> Optional[ArtifactEnvelope]:
        """Get artifact by ID string."""
        pass
    
    @abstractmethod
    def get_latest(self, name: str) -> Optional[ArtifactEnvelope]:
        """Get latest artifact by name."""
        pass
    
    @abstractmethod
    def get_history(self, name: str) -> List[ArtifactEnvelope]:
        """Get all versions by name."""
        pass
    
    @abstractmethod
    def verify_all(self) -> List[str]:
        """Verify all artifacts in store."""
        pass
    
    @abstractmethod
    def get_append_log(self) -> List[ArtifactEnvelope]:
        """Get append log."""
        pass


class InMemoryArtifactStore(ArtifactStore):
    """In-memory implementation of artifact store."""
    
    def __init__(self):
        self._artifacts_by_id: Dict[str, ArtifactEnvelope] = {}
        self._artifacts_by_name: Dict[str, List[ArtifactEnvelope]] = {}
        self._append_log: List[ArtifactEnvelope] = []
    
    def append(self, envelope: ArtifactEnvelope) -> ArtifactId:
        artifact_id = envelope.artifact_id.value
        
        if artifact_id in self._artifacts_by_id:
            return envelope.artifact_id
        
        if not envelope.verify():
            raise ValueError(f"Checksum verification failed for artifact {artifact_id}")
        
        self._artifacts_by_id[artifact_id] = envelope
        if envelope.name not in self._artifacts_by_name:
            self._artifacts_by_name[envelope.name] = []
        self._artifacts_by_name[envelope.name].append(envelope)
        self._append_log.append(envelope)
        
        return envelope.artifact_id
    
    def get(self, artifact_id: ArtifactId) -> Optional[ArtifactEnvelope]:
        return self._artifacts_by_id.get(artifact_id.value)
    
    def get_by_id(self, artifact_id: str) -> Optional[ArtifactEnvelope]:
        return self._artifacts_by_id.get(artifact_id)
    
    def get_latest(self, name: str) -> Optional[ArtifactEnvelope]:
        artifacts = self._artifacts_by_name.get(name, [])
        return artifacts[-1] if artifacts else None
    
    def get_history(self, name: str) -> Tuple[ArtifactEnvelope, ...]:
        return tuple(self._artifacts_by_name.get(name, ()))
    
    def verify_all(self) -> List[str]:
        failed = []
        for artifact_id, envelope in self._artifacts_by_id.items():
            if not envelope.verify():
                failed.append(artifact_id)
        return failed
    
    def get_append_log(self) -> List[ArtifactEnvelope]:
        return self._append_log.copy()
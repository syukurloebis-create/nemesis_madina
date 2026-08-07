"""
Immutable Append-Only Artifact Store.
Phase 1 - Core Infrastructure
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict

from .contracts import ArtifactId, ArtifactEnvelope


class AppendOnlyArtifactStore:
    """
    Immutable append-only artifact store.
    """
    
    def __init__(self):
        self._artifacts_by_id: Dict[str, ArtifactEnvelope] = {}
        self._artifacts_by_name: Dict[str, List[ArtifactEnvelope]] = defaultdict(list)
        self._append_log: List[ArtifactEnvelope] = []
    
    def append(self, envelope: ArtifactEnvelope) -> ArtifactId:
        """Append an artifact to the store."""
        artifact_id = envelope.artifact_id.value
        
        if artifact_id in self._artifacts_by_id:
            return envelope.artifact_id
        
        if not envelope.verify():
            raise ValueError(f"Checksum verification failed for artifact {artifact_id}")
        
        self._artifacts_by_id[artifact_id] = envelope
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
    
    def get_history(self, name: str) -> List[ArtifactEnvelope]:
        return self._artifacts_by_name.get(name, [])
    
    def get_append_log(self) -> List[ArtifactEnvelope]:
        return self._append_log.copy()
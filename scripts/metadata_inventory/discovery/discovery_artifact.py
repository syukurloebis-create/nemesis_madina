# scripts/metadata_inventory/discovery/discovery_artifact.py
"""
Discovery Artifacts - Normalized, sorted, deterministic artifacts.
Phase 2.5 - Discovery Stabilization
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from ..canonical_serializer import Fingerprint


@dataclass(frozen=True)
class NormalizedTableInfo:
    """Normalized table information."""
    name: str
    schema: Optional[str] = None
    columns: Tuple[str, ...] = ()
    primary_keys: Tuple[str, ...] = ()
    foreign_keys: Tuple[Dict[str, str], ...] = ()
    indexes: Tuple[str, ...] = ()


@dataclass(frozen=True)
class NormalizedModelInfo:
    """Normalized model information."""
    name: str
    module: str
    tablename: Optional[str] = None
    is_abstract: bool = False
    column_count: int = 0
    primary_keys: Tuple[str, ...] = ()
    foreign_keys: Tuple[Dict[str, str], ...] = ()
    relationships: Tuple[Dict[str, str], ...] = ()


@dataclass(frozen=True)
class RegistryArtifact:
    """Artifact dari registry discovery."""
    fingerprint: str
    canonical_fingerprint: str
    namespace: str
    registry_count: int
    table_count: int
    mapper_count: int
    tables: Tuple[str, ...]
    table_infos: Tuple[NormalizedTableInfo, ...] = ()
    model_infos: Tuple[NormalizedModelInfo, ...] = ()
    is_canonical: bool = True
    discovery_method: str = "canonical"
    checksum: str = ""
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'RegistryArtifact':
        """Reconstruct from payload."""
        return cls(
            fingerprint=payload.get("fingerprint", ""),
            canonical_fingerprint=payload.get("canonical_fingerprint", ""),
            namespace=payload.get("namespace", ""),
            registry_count=payload.get("registry_count", 0),
            table_count=payload.get("table_count", 0),
            mapper_count=payload.get("mapper_count", 0),
            tables=tuple(payload.get("tables", [])),
            is_canonical=payload.get("is_canonical", True),
            discovery_method=payload.get("discovery_method", "canonical"),
            checksum=payload.get("checksum", "")
        )
    
    def to_payload(self) -> Dict[str, Any]:
        """Serialize to payload."""
        return {
            "fingerprint": self.fingerprint,
            "canonical_fingerprint": self.canonical_fingerprint,
            "namespace": self.namespace,
            "registry_count": self.registry_count,
            "table_count": self.table_count,
            "mapper_count": self.mapper_count,
            "tables": list(self.tables),
            "is_canonical": self.is_canonical,
            "discovery_method": self.discovery_method,
            "checksum": self.checksum
        }


@dataclass(frozen=True)
class DiscoveryArtifact:
    fingerprint: str
    checksum: str
    timestamp: str
    import_fingerprint: str
    registry_fingerprint: str
    registry_count: int = 0
    model_count: int = 0
    table_count: int = 0
    mapper_count: int = 0
    payload_version: str = "1.0"
    
    @classmethod
    def create(
        cls,
        import_fingerprint: str,
        registry_fingerprint: str
    ) -> 'DiscoveryArtifact':
        """Create DiscoveryArtifact from fingerprints."""
        from datetime import datetime
        from ..canonical_serializer import Fingerprint

        # Validasi tipe
        if not isinstance(import_fingerprint, str):
            raise TypeError(f"import_fingerprint must be str, got {type(import_fingerprint)}")
        if not isinstance(registry_fingerprint, str):
            raise TypeError(f"registry_fingerprint must be str, got {type(registry_fingerprint)}")
        
        timestamp = datetime.now().isoformat()
        
        # 1. FINGERPRINT = identity (only fingerprints)
        identity = {
            "import_fingerprint": import_fingerprint,
            "registry_fingerprint": registry_fingerprint
        }
        fingerprint = Fingerprint.generate(identity)
        
        # 2. CHECKSUM = integrity (full payload)
        integrity = {
            "payload_version": "1.0",
            "timestamp": timestamp,
            "fingerprint": fingerprint,
            "import_fingerprint": import_fingerprint,
            "registry_fingerprint": registry_fingerprint,
            "registry_count": 0,
            "model_count": 0,
            "table_count": 0,
            "mapper_count": 0
        }
        checksum = Fingerprint.generate(integrity)  # DIFFERENT from fingerprint
        
        return cls(
            fingerprint=fingerprint,
            checksum=checksum,  # <-- NOW DIFFERENT
            timestamp=timestamp,
            import_fingerprint=import_fingerprint,
            registry_fingerprint=registry_fingerprint,
            registry_count=0,
            model_count=0,
            table_count=0,
            mapper_count=0,
            payload_version="1.0"
        )
    
    def identity_payload(self) -> Dict[str, Any]:
        return {
            "import_fingerprint": self.import_fingerprint,
            "registry_fingerprint": self.registry_fingerprint
        }
    
    def verify_identity(self) -> bool:
        from ..canonical_serializer import Fingerprint
        expected = Fingerprint.generate(self.identity_payload())
        return self.fingerprint == expected
    
    def verify_integrity(self) -> bool:
        from ..canonical_serializer import Fingerprint
        
        # Build integrity payload (full payload WITHOUT checksum)
        integrity = {
            "payload_version": self.payload_version,
            "timestamp": self.timestamp,
            "fingerprint": self.fingerprint,
            "import_fingerprint": self.import_fingerprint,
            "registry_fingerprint": self.registry_fingerprint,
            "registry_count": self.registry_count,
            "model_count": self.model_count,
            "table_count": self.table_count,
            "mapper_count": self.mapper_count
        }
        expected = Fingerprint.generate(integrity)
        return self.checksum == expected
    
    def verify(self) -> bool:
        return self.verify_identity() and self.verify_integrity()
    
    def to_payload(self) -> Dict[str, Any]:
        """Serialize to payload."""
        return {
            "payload_version": self.payload_version,
            "timestamp": self.timestamp,
            "fingerprint": self.fingerprint,
            "checksum": self.checksum,
            "import_fingerprint": self.import_fingerprint,
            "registry_fingerprint": self.registry_fingerprint,
            "registry_count": self.registry_count,
            "model_count": self.model_count,
            "table_count": self.table_count,
            "mapper_count": self.mapper_count
        }
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'DiscoveryArtifact':
        """Reconstruct from payload."""
        return cls(
            fingerprint=payload.get("fingerprint", ""),
            checksum=payload.get("checksum", ""),
            timestamp=payload.get("timestamp", ""),
            import_fingerprint=payload.get("import_fingerprint", ""),
            registry_fingerprint=payload.get("registry_fingerprint", ""),
            registry_count=payload.get("registry_count", 0),
            model_count=payload.get("model_count", 0),
            table_count=payload.get("table_count", 0),
            mapper_count=payload.get("mapper_count", 0),
            payload_version=payload.get("payload_version", "1.0")
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "RegistryArtifact",
    "DiscoveryArtifact",
    "NormalizedTableInfo",
    "NormalizedModelInfo",
]
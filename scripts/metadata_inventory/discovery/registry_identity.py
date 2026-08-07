# scripts/metadata_inventory/discovery/registry_identity.py
"""
Registry Identity - Fingerprint-based registry identification.
Phase 2 - Discovery Runtime (Revised)
"""

import hashlib
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field

from ..canonical_serializer import CanonicalSerializer


@dataclass(frozen=True)
class RegistryFingerprint:
    """
    Stable fingerprint for a registry.
    NOT dependent on process-local id().
    Stable across processes and machines.
    """
    namespace: str
    metadata_hash: str
    tables_hash: str
    mappers_hash: str
    combined_hash: str
    
    @classmethod
    def from_registry(cls, registry, namespace: Optional[str] = None) -> 'RegistryFingerprint':
        """Generate fingerprint from a SQLAlchemy registry."""
        # Tables: sorted by name
        tables = sorted(registry.metadata.tables.keys())
        tables_hash = hashlib.sha256(
            CanonicalSerializer.serialize(tables).encode()
        ).hexdigest()[:16]
        
        # Mappers: sorted by class name + module
        mappers = sorted([
            f"{m.class_.__module__}.{m.class_.__name__}"
            for m in registry.mappers
            if hasattr(m, 'class_') and m.class_
        ])
        mappers_hash = hashlib.sha256(
            CanonicalSerializer.serialize(mappers).encode()
        ).hexdigest()[:16]
        
        # Metadata: only stable info (NO id())
        metadata_info = {
            "tables": tables,
            "mappers": mappers
        }
        metadata_hash = hashlib.sha256(
            CanonicalSerializer.serialize(metadata_info).encode()
        ).hexdigest()[:16]
        
        # Combined
        combined = f"{metadata_hash}:{tables_hash}:{mappers_hash}"
        combined_hash = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        return cls(
            namespace=namespace or "default",
            metadata_hash=metadata_hash,
            tables_hash=tables_hash,
            mappers_hash=mappers_hash,
            combined_hash=combined_hash
        )
    
    def __str__(self) -> str:
        return self.combined_hash
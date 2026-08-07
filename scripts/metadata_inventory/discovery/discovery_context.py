# scripts/metadata_inventory/discovery/discovery_context.py
"""
DiscoveryContext - Immutable runtime object for discovery data.
Phase 2 - Discovery Runtime
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from .registry_identity import RegistryFingerprint
from .model_discovery import ModelMetadata


@dataclass(frozen=True)
class DiscoveryContext:
    """
    Immutable runtime context for discovery.
    Passed between DAG nodes.
    """
    # Registry
    registry: Any  # SQLAlchemy registry object
    fingerprint: RegistryFingerprint
    fingerprint_str: str
    is_canonical: bool
    
    # Models
    models: Tuple[ModelMetadata, ...] = ()
    
    # Modules
    imported_modules: Tuple[str, ...] = ()
    
    # Summary
    table_count: int = 0
    mapper_count: int = 0
    model_count: int = 0
    
    # Metadata
    discovery_method: str = "canonical"
    
    @classmethod
    def from_registry(cls, registry, is_canonical: bool = True, discovery_method: str = "canonical") -> 'DiscoveryContext':
        """Create context from a registry."""
        fingerprint = RegistryFingerprint.from_registry(registry)
        fingerprint_str = str(fingerprint)
        
        tables = list(registry.metadata.tables.keys()) if hasattr(registry, 'metadata') else []
        mappers = list(registry.mappers) if hasattr(registry, 'mappers') else []
        
        return cls(
            registry=registry,
            fingerprint=fingerprint,
            fingerprint_str=fingerprint_str,
            is_canonical=is_canonical,
            table_count=len(tables),
            mapper_count=len(mappers),
            discovery_method=discovery_method
        )
    
    def with_models(self, models: List[ModelMetadata]) -> 'DiscoveryContext':
        """Return new context with models added."""
        return DiscoveryContext(
            registry=self.registry,
            fingerprint=self.fingerprint,
            fingerprint_str=self.fingerprint_str,
            is_canonical=self.is_canonical,
            models=tuple(models),
            imported_modules=self.imported_modules,
            table_count=self.table_count,
            mapper_count=self.mapper_count,
            model_count=len(models),
            discovery_method=self.discovery_method
        )
    
    def with_imported_modules(self, modules: List[str]) -> 'DiscoveryContext':
        """Return new context with imported modules added."""
        return DiscoveryContext(
            registry=self.registry,
            fingerprint=self.fingerprint,
            fingerprint_str=self.fingerprint_str,
            is_canonical=self.is_canonical,
            models=self.models,
            imported_modules=tuple(modules),
            table_count=self.table_count,
            mapper_count=self.mapper_count,
            model_count=self.model_count,
            discovery_method=self.discovery_method
        )
    
    def to_summary(self) -> Dict[str, Any]:
        """Get summary of the context."""
        return {
            "fingerprint": self.fingerprint_str,
            "is_canonical": self.is_canonical,
            "table_count": self.table_count,
            "mapper_count": self.mapper_count,
            "model_count": self.model_count,
            "discovery_method": self.discovery_method
        }
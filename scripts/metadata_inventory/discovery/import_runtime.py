# scripts/metadata_inventory/discovery/import_runtime.py
"""
Import Runtime - Audit dan import semua model modules.
Phase 2.5 - Discovery Stabilization
"""

import sys
import importlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from .provenance import ModuleProvenance
from ..canonical_serializer import Fingerprint


@dataclass(frozen=True)
class ModuleMetadata:
    """Pure DTO for module metadata (JSON serializable)."""
    module: str
    origin: str
    loader_name: str
    is_package: bool
    
    @classmethod
    def from_module(cls, module, module_name: str) -> 'ModuleMetadata':
        """Create metadata from a Python module object."""
        return cls(
            module=module_name,
            origin=getattr(module, '__file__', 'unknown') or 'unknown',
            loader_name=getattr(getattr(module, '__loader__', None), '__name__', 'unknown'),
            is_package=getattr(module, '__package__', None) == module_name
        )


@dataclass(frozen=True)
class ImportArtifact:
    """Artifact dari import runtime - PURE DTO (JSON serializable)."""
    imported_modules: Tuple[str, ...]
    failed_modules: Tuple[str, ...]
    mappers_before: int
    mappers_after: int
    mapper_growth: int
    fingerprint: str
    module_metadata: Tuple[ModuleMetadata, ...] = ()  # Pure DTO, not ModuleSpec
    
    @classmethod
    def create(cls, modules: List[str]) -> 'ImportArtifact':
        """Create import artifact from module list."""
        from ..canonical_serializer import Fingerprint
        
        imported = []
        failed = []
        metadata_list = []
        mappers_before = 0
        mappers_after = 0
        
        # Get initial state
        try:
            from backend.database import Base
            mappers_before = len(Base.registry.mappers) if hasattr(Base, 'registry') else 0
        except Exception:
            pass
        
        # Import each module with provenance
        for module_name in modules:
            try:
                module = __import__(module_name)
                imported.append(module_name)
                
                # Collect metadata as pure DTO
                metadata_list.append(
                    ModuleMetadata.from_module(module, module_name)
                )
            except Exception:
                failed.append(module_name)
        
        # Get final state
        try:
            from backend.database import Base
            mappers_after = len(Base.registry.mappers) if hasattr(Base, 'registry') else 0
        except Exception:
            pass
        
        # Generate fingerprint
        content = {
            "imported": sorted(imported),
            "failed": sorted(failed),
            "mappers_before": mappers_before,
            "mappers_after": mappers_after
        }
        fingerprint = Fingerprint.generate(content)
        
        return cls(
            imported_modules=tuple(imported),
            failed_modules=tuple(failed),
            mappers_before=mappers_before,
            mappers_after=mappers_after,
            mapper_growth=mappers_after - mappers_before,
            fingerprint=fingerprint,
            module_metadata=tuple(metadata_list)
        )
    
    def to_payload(self) -> Dict[str, Any]:
        """Serialize to payload (JSON serializable)."""
        return {
            "imported": list(self.imported_modules),
            "failed": list(self.failed_modules),
            "mappers_before": self.mappers_before,
            "mappers_after": self.mappers_after,
            "mapper_growth": self.mapper_growth,
            "fingerprint": self.fingerprint,
            "module_metadata": [
                {
                    "module": m.module,
                    "origin": m.origin,
                    "loader_name": m.loader_name,
                    "is_package": m.is_package
                }
                for m in self.module_metadata
            ]
        }
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'ImportArtifact':
        """Reconstruct ImportArtifact from serialized payload."""
        metadata = []
        for m in payload.get("module_metadata", []):
            metadata.append(ModuleMetadata(
                module=m.get("module", ""),
                origin=m.get("origin", "unknown"),
                loader_name=m.get("loader_name", "unknown"),
                is_package=m.get("is_package", False)
            ))
        
        return cls(
            imported_modules=tuple(payload.get("imported", [])),
            failed_modules=tuple(payload.get("failed", [])),
            mappers_before=payload.get("mappers_before", 0),
            mappers_after=payload.get("mappers_after", 0),
            mapper_growth=payload.get("mapper_growth", 0),
            fingerprint=payload.get("fingerprint", ""),
            module_metadata=tuple(metadata)
        )
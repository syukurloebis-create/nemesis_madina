# scripts/metadata_inventory/discovery/provenance.py
"""
Module Provenance - Immutable provenance information.
Phase 2.5 - Final Semantic Closure
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModuleProvenance:
    """Immutable provenance information for an imported module."""
    module: str
    origin: str  # __file__ path
    loader_name: str
    is_package: bool
    
    @classmethod
    def from_module(cls, module, module_name: str) -> 'ModuleProvenance':
        """Create provenance from a Python module object."""
        return cls(
            module=module_name,
            origin=getattr(module, '__file__', 'unknown') or 'unknown',
            loader_name=getattr(getattr(module, '__loader__', None), '__name__', 'unknown'),
            is_package=getattr(module, '__package__', None) == module_name
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "module": self.module,
            "origin": self.origin,
            "loader_name": self.loader_name,
            "is_package": str(self.is_package)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'ModuleProvenance':
        """Create from dictionary."""
        return cls(
            module=data.get("module", ""),
            origin=data.get("origin", "unknown"),
            loader_name=data.get("loader_name", "unknown"),
            is_package=data.get("is_package", "false").lower() == "true"
        )
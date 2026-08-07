# scripts/metadata_inventory/context.py
from typing import Mapping, Sequence
from typing import Dict, List, Optional, Any, Callable, Type
from pathlib import Path
from types import MappingProxyType

@dataclass(frozen=True)
class PipelineContext:
    """
    PipelineContext - read-only contract.
    Menggunakan immutable collections.
    """
    # Mode
    mode: AuditMode
    
    # Paths
    output_dir: Path
    project_root: Path
    
    # Versions
    contract_version: str = CONTRACT_VERSION
    
    # Discovery
    discovery_result: Optional[Mapping[str, object]] = None
    
    # Configuration (read-only)
    config: Mapping[str, object] = MappingProxyType({})
    weights: Mapping[str, object] = MappingProxyType({})
    
    # Baseline (read-only)
    baseline: Optional[Mapping[str, object]] = None
    baseline_fingerprint: Optional[str] = None
    
    # Runtime options (read-only)
    runtime_options: Mapping[str, object] = MappingProxyType({})
    
    # Plugins (tuple, immutable)
    enabled_plugins: Sequence[str] = ()
    
    # Logger
    log_path: Optional[Path] = None
    
    @classmethod
    def create(cls, **kwargs) -> 'PipelineContext':
        """Factory method untuk memastikan immutable collections."""
        # Konversi dict ke MappingProxyType untuk read-only
        for key in ['config', 'weights', 'runtime_options']:
            if key in kwargs and isinstance(kwargs[key], dict):
                kwargs[key] = MappingProxyType(kwargs[key])
        
        # Konversi list ke tuple
        if 'enabled_plugins' in kwargs and isinstance(kwargs['enabled_plugins'], list):
            kwargs['enabled_plugins'] = tuple(kwargs['enabled_plugins'])
        
        return cls(**kwargs)
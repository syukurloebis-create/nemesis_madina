"""
Canonical Serializer - Deterministic serialization.
Phase 1 - Core Infrastructure
"""

import json
import uuid
import decimal
from datetime import datetime, date, time
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Type 
from dataclasses import is_dataclass, asdict
import hashlib


# scripts/metadata_inventory/canonical_serializer.py (Final)
from typing import Callable, List, Any, Mapping
from types import MappingProxyType
import hashlib


def sha256_v1(data: str) -> str:
    """SHA256 fingerprint with 16-character truncation."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def sha256_full(data: str) -> str:
    """Full SHA256 fingerprint (64 characters)."""
    return hashlib.sha256(data.encode()).hexdigest()


class Fingerprint:
    """
    Deterministic fingerprint generator with explicit algorithm.
    
    Algorithm registry is IMMUTABLE - no runtime registration.
    New algorithms require code change (explicit design decision).
    """
    
    # Immutable algorithm registry
    ALGORITHMS: Mapping[str, Callable[[str], str]] = MappingProxyType({
        "sha256-v1": sha256_v1,
        "sha256-full": sha256_full,
    })
    
    @staticmethod
    def generate(obj: Any, algorithm: str = "sha256-v1") -> str:
        if algorithm not in Fingerprint.ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Normalize object to JSON-serializable
        normalized = Fingerprint._normalize(obj)
        canonical = CanonicalSerializer.serialize(normalized)
        return Fingerprint.ALGORITHMS[algorithm](canonical)
    
    @staticmethod
    def _normalize(obj: Any) -> Any:
        """Normalize object to JSON-serializable primitive."""
        from dataclasses import is_dataclass, asdict
        from pathlib import Path
        from datetime import datetime
        from enum import Enum
        
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        if hasattr(obj, 'value') and isinstance(obj.value, str):
            return obj.value
        if is_dataclass(obj):
            return Fingerprint._normalize(asdict(obj))
        if isinstance(obj, (tuple, list)):
            return [Fingerprint._normalize(item) for item in obj]
        if isinstance(obj, dict):
            return {str(k): Fingerprint._normalize(v) for k, v in obj.items()}
        if hasattr(obj, '__dict__'):
            return Fingerprint._normalize(obj.__dict__)
        return str(obj)
    
    @staticmethod
    def list_algorithms() -> List[str]:
        """List all available algorithms."""
        return list(Fingerprint.ALGORITHMS.keys())

class CanonicalSerializer:
    """Deterministic serializer for all types."""
    
    @staticmethod
    def serialize(obj: Any) -> str:
        return json.dumps(
            CanonicalSerializer._to_canonical(obj),
            sort_keys=True,
            separators=(',', ':')
        )
    
    @staticmethod
    def _to_canonical(obj: Any) -> Any:
        if obj is None:
            return None
        
        if isinstance(obj, (str, int, float, bool)):
            return obj
        
        if isinstance(obj, Enum):
            return obj.value
        
        if isinstance(obj, uuid.UUID):
            return str(obj)
        
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        
        if isinstance(obj, datetime):
            if obj.tzinfo is None:
                obj = obj.replace(tzinfo=datetime.UTC)
            return obj.isoformat().replace('+00:00', 'Z')
        
        if isinstance(obj, date):
            return obj.isoformat()
        
        if isinstance(obj, time):
            return obj.isoformat()
        
        if is_dataclass(obj):
            return {
                k: CanonicalSerializer._to_canonical(v)
                for k, v in asdict(obj).items()
                if not k.startswith('_')
            }
        
        if isinstance(obj, list):
            return [CanonicalSerializer._to_canonical(item) for item in obj]
        
        if isinstance(obj, tuple):
            return [CanonicalSerializer._to_canonical(item) for item in obj]
        
        if isinstance(obj, set):
            return sorted(
                [CanonicalSerializer._to_canonical(item) for item in obj],
                key=lambda x: json.dumps(x, sort_keys=True)
            )
        
        if isinstance(obj, dict):
            return {
                str(k): CanonicalSerializer._to_canonical(v)
                for k, v in sorted(obj.items())
            }
        
        return str(obj)
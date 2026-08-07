# scripts/metadata_inventory/contracts/versioning.py
"""
Versioning Contracts - Independent versions for payload, identity, and checksum.
Phase 2.5 - Production Hardening
"""

from typing import Dict, List, Optional, Any, Callable, Type
from types import MappingProxyType
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ArtifactVersions:
    """Independent versions for artifact components."""
    payload_version: str = "1.0"
    identity_version: str = "sha256-v1"
    checksum_version: str = "sha256-v1"
    
    # Compatibility matrix - IMMUTABLE using MappingProxyType
    _COMPATIBILITY_MATRIX = MappingProxyType({
        "sha256-v1": ("sha256-v1",),
        "sha256-full": ("sha256-full",),
        "blake3-v1": ("blake3-v1",),
    })
    
    @classmethod
    def get_compatibility_matrix(cls) -> MappingProxyType:
        """Get the immutable compatibility matrix."""
        return cls._COMPATIBILITY_MATRIX
    
    def to_payload(self) -> Dict[str, str]:
        """Serialize to payload."""
        return {
            "payload_version": self.payload_version,
            "identity_version": self.identity_version,
            "checksum_version": self.checksum_version
        }
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> 'ArtifactVersions':
        """Reconstruct from payload."""
        return cls(
            payload_version=payload.get("payload_version", "1.0"),
            identity_version=payload.get("identity_version", "sha256-v1"),
            checksum_version=payload.get("checksum_version", "sha256-v1")
        )
    
    def is_compatible(self, other: 'ArtifactVersions') -> bool:
        """
        Check compatibility with another version set.
        
        Rules:
        1. Payload version must match exactly
        2. Identity version must be compatible (same algorithm family)
        3. Checksum version must be compatible (same algorithm family)
        """
        # Payload version must match exactly
        if self.payload_version != other.payload_version:
            return False
        
        # Identity version compatibility
        if self.identity_version != other.identity_version:
            if self.identity_version not in self._COMPATIBILITY_MATRIX:
                return False
            if other.identity_version not in self._COMPATIBILITY_MATRIX:
                return False
            if other.identity_version not in self._COMPATIBILITY_MATRIX[self.identity_version]:
                return False
        
        # Checksum version compatibility
        if self.checksum_version != other.checksum_version:
            if self.checksum_version not in self._COMPATIBILITY_MATRIX:
                return False
            if other.checksum_version not in self._COMPATIBILITY_MATRIX:
                return False
            if other.checksum_version not in self._COMPATIBILITY_MATRIX[self.checksum_version]:
                return False
        
        return True
    
    @classmethod
    def is_version_known(cls, version: str) -> bool:
        """Check if a version is known in the compatibility matrix."""
        return version in cls._COMPATIBILITY_MATRIX
    
    @classmethod
    def add_compatibility(cls, version: str, compatible_with: List[str]) -> None:
        """Add compatibility entry for a version."""
        # Note: This modifies the matrix, but it's a class method
        # For production, consider using a mutable copy if needed
        cls._COMPATIBILITY_MATRIX = MappingProxyType({
            **cls._COMPATIBILITY_MATRIX,
            version: tuple(compatible_with)
        })
# scripts/tests/test_serialization_roundtrip.py
"""
Serialization Round-Trip Tests.
Phase 2.5 - Production Hardening
"""

import json
import pytest
from typing import Dict, List, Any, Optional, Tuple

from metadata_inventory.discovery.import_runtime import ImportArtifact
from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact

pytestmark = pytest.mark.unit


class TestSerializationRoundtrip:
    """Test serialization roundtrip."""
    
    def test_import_discovery_artifacts(self):
        """Test discovery_artifacts import works."""
        from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact
        assert RegistryArtifact is not None
        assert DiscoveryArtifact is not None


class MockRegistry:
    def __init__(self, tables=None, mappers=None):
        self.tables = tables or []
        self.mappers = mappers or []
        self.metadata = MockMetadata(tables)


class MockMetadata:
    def __init__(self, tables=None):
        self._tables = {t: MockTable(t) for t in (tables or [])}
    
    @property
    def tables(self):
        return self._tables


class MockTable:
    def __init__(self, name, schema=None):
        self.name = name
        self.schema = schema
        self.columns = []
        self.primary_key = MockPrimaryKey()
        self.indexes = []


class MockPrimaryKey:
    def __init__(self):
        self.columns = []


class MockMapper:
    def __init__(self, name, module, table_name):
        self.class_ = MockClass(name, module)
        self.local_table = MockTable(table_name)
        self.columns = []
        self.relationships = []


class MockClass:
    def __init__(self, name, module):
        self.__name__ = name
        self.__module__ = module


def create_mock_registry(namespace: str, tables: List[str], mappers: List[tuple]) -> object:
    registry = MockRegistry(tables)
    registry.mappers = [
        MockMapper(name, module, table)
        for name, module, table in mappers
    ]
    return registry


def test_serialization_roundtrip():
    """Test that serialization roundtrip preserves artifact integrity."""
    
    # Create original artifact
    import_artifact = ImportArtifact.create(["backend.models.user"])
    
    mock_registry = create_mock_registry(
        namespace="backend.database",
        tables=["users"],
        mappers=[("User", "backend.models.user", "users")]
    )
    
    registry_artifact = RegistryArtifact.from_registry(
        registry=mock_registry,
        namespace="backend.database",
        is_canonical=True,
        discovery_method="canonical"
    )
    
    original = DiscoveryArtifact.create(import_artifact, registry_artifact)
    
    # Serialize to JSON
    payload = original.to_payload()
    json_str = json.dumps(payload, default=str)
    
    # Deserialize from JSON
    loaded_payload = json.loads(json_str)
    reconstructed = DiscoveryArtifact.from_payload(loaded_payload)
    
    # Verify integrity
    assert reconstructed.verify_identity()
    assert reconstructed.verify_integrity()
    assert reconstructed.verify()
    
    # Verify all fields match
    assert reconstructed.fingerprint == original.fingerprint
    assert reconstructed.checksum == original.checksum
    assert reconstructed.payload_version == original.payload_version
    assert reconstructed.identity_version == original.identity_version
    assert reconstructed.checksum_version == original.checksum_version


def test_serialization_roundtrip_with_multiple_versions():
    """Test serialization roundtrip with different version combinations."""
    
    import_artifact = ImportArtifact.create(["backend.models.user"])
    
    mock_registry = create_mock_registry(
        namespace="backend.database",
        tables=["users"],
        mappers=[("User", "backend.models.user", "users")]
    )
    
    registry_artifact = RegistryArtifact.from_registry(
        registry=mock_registry,
        namespace="backend.database",
        is_canonical=True,
        discovery_method="canonical"
    )
    
    # Test with different version combinations
    versions = [
        ("sha256-v1", "sha256-v1"),
        ("sha256-full", "sha256-full"),
    ]
    
    for identity_version, checksum_version in versions:
        original = DiscoveryArtifact.create(
            import_artifact,
            registry_artifact,
            identity_version=identity_version,
            checksum_version=checksum_version
        )
        
        payload = original.to_payload()
        json_str = json.dumps(payload, default=str)
        loaded_payload = json.loads(json_str)
        reconstructed = DiscoveryArtifact.from_payload(loaded_payload)
        
        assert reconstructed.verify()
        assert reconstructed.fingerprint == original.fingerprint
        assert reconstructed.checksum == original.checksum


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
# scripts/tests/test_invariants.py
"""
Invariant Tests - Verify artifact integrity under tampering.
Phase 2.5 - Production Hardening
"""

import pytest
from typing import Dict, List, Any, Optional, Tuple

from metadata_inventory.discovery.import_runtime import ImportArtifact
from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact
from metadata_inventory.discovery.registry_identity import RegistryFingerprint
from metadata_inventory.canonical_serializer import Fingerprint

pytestmark = pytest.mark.unit


class TestInvariants:
    """Test invariants."""
    
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


def test_identity_invariant():
    """Test that fingerprint is immutable to semantic changes that don't affect identity."""
    
    # Create artifact
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
    
    discovery = DiscoveryArtifact.create(import_artifact, registry_artifact)
    
    # Identity verification passes initially
    assert discovery.verify_identity()
    
    # Tamper with raw semantic state in transport payload
    payload = discovery.to_payload()
    payload["registry"]["tables"].append("evil")  # Tampering
    
    # Reconstruct from tampered payload
    tampered = DiscoveryArtifact.from_payload(payload)
    
    # Identity should still pass (identity only uses fingerprints, not raw tables)
    # But integrity should fail (checksum covers raw tables)
    assert tampered.verify_identity() is True
    assert tampered.verify_integrity() is False
    assert tampered.verify() is False


def test_timestamp_invariant():
    """Test that timestamp changes don't affect identity."""
    
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
    
    discovery = DiscoveryArtifact.create(import_artifact, registry_artifact)
    
    # Identity doesn't include timestamp
    payload = discovery.to_payload()
    payload["timestamp"] = "different_timestamp"
    
    tampered = DiscoveryArtifact.from_payload(payload)
    
    # Identity should still pass
    assert tampered.verify_identity() is True
    # Integrity should fail (timestamp is in integrity payload)
    assert tampered.verify_integrity() is False


def test_child_fingerprint_invariant():
    """Test that changing child fingerprint changes aggregate identity."""
    
    import_artifact_1 = ImportArtifact.create(["backend.models.user"])
    import_artifact_2 = ImportArtifact.create(["backend.models.user", "backend.models.order"])
    
    mock_registry = create_mock_registry(
        namespace="backend.database",
        tables=["users", "orders"],
        mappers=[
            ("User", "backend.models.user", "users"),
            ("Order", "backend.models.order", "orders")
        ]
    )
    
    registry_artifact = RegistryArtifact.from_registry(
        registry=mock_registry,
        namespace="backend.database",
        is_canonical=True,
        discovery_method="canonical"
    )
    
    discovery_1 = DiscoveryArtifact.create(import_artifact_1, registry_artifact)
    discovery_2 = DiscoveryArtifact.create(import_artifact_2, registry_artifact)
    
    # Different import fingerprint → different discovery fingerprint
    assert discovery_1.fingerprint != discovery_2.fingerprint


def test_checksum_invariant():
    """Test that checksum catches any payload modification."""
    
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
    
    discovery = DiscoveryArtifact.create(import_artifact, registry_artifact)
    
    # Tamper with checksum itself
    payload = discovery.to_payload()
    payload["checksum"] = "tampered_checksum"
    
    tampered = DiscoveryArtifact.from_payload(payload)
    
    # verify() should fail
    assert tampered.verify() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
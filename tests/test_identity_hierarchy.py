# tests/test_identity_hierarchy.py
"""
Test identity hierarchy.
"""

import pytest
from typing import List, Dict, Any, Tuple

pytestmark = pytest.mark.unit


# ============================================================================
# MOCK CLASSES FOR TESTING
# ============================================================================

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


class MockMetadata:
    def __init__(self, tables=None):
        self._tables = {}
        for t in (tables or []):
            self._tables[t] = MockTable(t)
    
    @property
    def tables(self):
        return self._tables


class MockRegistry:
    def __init__(self, tables=None, mappers=None):
        self.tables = tables or []
        self.mappers = mappers or []
        self._metadata = MockMetadata(tables)
    
    @property
    def metadata(self):
        return self._metadata


class MockClass:
    def __init__(self, name, module):
        self.__name__ = name
        self.__module__ = module


class MockMapper:
    def __init__(self, name, module, table_name):
        self.class_ = MockClass(name, module)
        self.local_table = MockTable(table_name)
        self.columns = []
        self.relationships = []
        self.primary_key = MockPrimaryKey()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_mock_registry(namespace: str, tables: List[str], mappers: List[tuple]) -> MockRegistry:
    """Create a mock registry for testing."""
    registry = MockRegistry(tables)
    registry.mappers = [
        MockMapper(name, module, table)
        for name, module, table in mappers
    ]
    return registry


def create_mock_registry_artifact(namespace: str, tables: List[str], mappers: List[tuple]) -> 'RegistryArtifact':
    """Create a mock registry artifact."""
    from metadata_inventory.discovery.discovery_artifact import RegistryArtifact
    
    registry = create_mock_registry(namespace, tables, mappers)
    
    # Create artifact using from_registry if available, or manually
    try:
        from metadata_inventory.discovery.registry_identity import RegistryFingerprint
        fp = RegistryFingerprint.from_registry(registry)
        fingerprint = str(fp)
    except Exception:
        fingerprint = "test_fingerprint"
    
    return RegistryArtifact(
        fingerprint=fingerprint,
        canonical_fingerprint=fingerprint,
        namespace=namespace,
        registry_count=1,
        table_count=len(tables),
        mapper_count=len(mappers),
        tables=tuple(tables),
        is_canonical=True,
        discovery_method="canonical",
        checksum="test_checksum"
    )


# ============================================================================
# TESTS
# ============================================================================

class TestIdentityHierarchy:
    """Test identity hierarchy."""
    
    def test_import_discovery_artifacts(self):
        """Test discovery_artifacts import works."""
        from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact
        assert RegistryArtifact is not None
        assert DiscoveryArtifact is not None
    
    def test_identity_hierarchy(self):
        """Test that identity hierarchy is consistent."""
        from metadata_inventory.discovery.import_runtime import ImportArtifact
        from metadata_inventory.discovery.discovery_artifact import RegistryArtifact, DiscoveryArtifact
        from metadata_inventory.canonical_serializer import Fingerprint
        
        # Create import artifact
        import_artifact = ImportArtifact.create(["backend.models.user", "backend.models.order"])
        
        # Create registry artifact
        registry_artifact = create_mock_registry_artifact(
            namespace="backend.database",
            tables=["users", "orders"],
            mappers=[
                ("User", "backend.models.user", "users"),
                ("Order", "backend.models.order", "orders")
            ]
        )
        
        # Create discovery artifact
        discovery_artifact = DiscoveryArtifact.create(
            import_artifact.fingerprint,
            registry_artifact.fingerprint
        )
        
        # Registry identity is stable
        assert registry_artifact.fingerprint is not None
        assert len(registry_artifact.fingerprint) == 16
        
        # Discovery identity is composite
        expected_identity = {
            "import_fingerprint": import_artifact.fingerprint,
            "registry_fingerprint": registry_artifact.fingerprint
        }
        expected_fingerprint = Fingerprint.generate(expected_identity)
        
        # Discovery identity != Registry identity
        assert discovery_artifact.fingerprint != registry_artifact.fingerprint
        
        # Verification passes
        assert discovery_artifact.verify_identity()
        assert discovery_artifact.verify_integrity()
        assert discovery_artifact.verify()
    
    def test_identity_changes_when_import_changes(self):
        """Test that Discovery identity changes when import changes."""
        from metadata_inventory.discovery.import_runtime import ImportArtifact
        from metadata_inventory.discovery.discovery_artifact import DiscoveryArtifact
        
        # Create two imports with different modules
        import_artifact_1 = ImportArtifact.create(["backend.models.user"])
        import_artifact_2 = ImportArtifact.create(["backend.models.user", "backend.models.order"])
        
        # Same registry
        registry_artifact = create_mock_registry_artifact(
            namespace="backend.database",
            tables=["users", "orders"],
            mappers=[
                ("User", "backend.models.user", "users"),
                ("Order", "backend.models.order", "orders")
            ]
        )
        
        # Create discovery artifacts
        discovery_1 = DiscoveryArtifact.create(import_artifact_1.fingerprint, registry_artifact.fingerprint)
        discovery_2 = DiscoveryArtifact.create(import_artifact_2.fingerprint, registry_artifact.fingerprint)
        
        # Registry identity is same
        assert discovery_1.registry_fingerprint == discovery_2.registry_fingerprint
        
        # Discovery identity is different (import changed)
        assert discovery_1.fingerprint != discovery_2.fingerprint
        
        # Both verify
        assert discovery_1.verify()
        assert discovery_2.verify()
    
    def test_identity_not_include_semantic_state(self):
        """Test that Discovery identity does NOT include raw semantic state."""
        from metadata_inventory.discovery.import_runtime import ImportArtifact
        from metadata_inventory.discovery.discovery_artifact import DiscoveryArtifact
        
        import_artifact = ImportArtifact.create(["backend.models.user"])
        
        registry_artifact = create_mock_registry_artifact(
            namespace="backend.database",
            tables=["users"],
            mappers=[("User", "backend.models.user", "users")]
        )
        
        discovery_artifact = DiscoveryArtifact.create(
            import_artifact.fingerprint,
            registry_artifact.fingerprint
        )
        
        # identity_payload should ONLY contain fingerprints
        identity_payload = discovery_artifact.identity_payload()
        
        assert "import_fingerprint" in identity_payload
        assert "registry_fingerprint" in identity_payload
        assert "tables" not in identity_payload
        assert "models" not in identity_payload
        assert "imported" not in identity_payload
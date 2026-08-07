# scripts/tests/conftest.py
"""
Shared fixtures for all tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any, List

from metadata_inventory.canonical_serializer import CanonicalSerializer, Fingerprint
from metadata_inventory.contracts import ArtifactId, ArtifactEnvelope
from metadata_inventory.discovery.registry_identity import RegistryFingerprint
from metadata_inventory.discovery.import_runtime import ImportArtifact
from metadata_inventory.discovery.discovery_artifacts import (
    RegistryArtifact, DiscoveryArtifact, NormalizedTableInfo, NormalizedModelInfo
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test output."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_payload():
    """Sample payload for testing."""
    return {
        "fingerprint": "a1b2c3d4e5f6g7h8",
        "checksum": "i9j0k1l2m3n4o5p6",
        "timestamp": "2026-08-05T12:00:00",
        "import": {
            "imported": ["backend.models.user", "backend.models.order"],
            "failed": [],
            "mappers_before": 0,
            "mappers_after": 2,
            "mapper_growth": 2
        },
        "registry": {
            "fingerprint": "r1s2t3u4v5w6x7y8",
            "canonical_fingerprint": "c1d2e3f4g5h6i7j8",
            "registry_count": 1,
            "table_count": 2,
            "mapper_count": 2,
            "tables": ["users", "orders"],
            "models": ["User", "Order"]
        }
    }


@pytest.fixture
def sample_artifact(sample_payload):
    """Create a sample DiscoveryArtifact."""
    from metadata_inventory.discovery.import_runtime import ImportArtifact
    from metadata_inventory.discovery.discovery_artifacts import RegistryArtifact, DiscoveryArtifact
    
    import_artifact = ImportArtifact.from_payload(sample_payload["import"])
    registry_artifact = RegistryArtifact.from_payload(sample_payload["registry"])
    
    return DiscoveryArtifact.create(import_artifact, registry_artifact)


@pytest.fixture
def mock_registry():
    """Create a mock registry for testing."""
    class MockMapper:
        def __init__(self, name, module, table_name):
            self.class_ = MockClass(name, module)
            self.local_table = MockTable(table_name)
            self.columns = []
            self.relationships = []
            self.primary_key = MockPrimaryKey()
    
    class MockClass:
        def __init__(self, name, module):
            self.__name__ = name
            self.__module__ = module
    
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
    
    class MockRegistry:
        def __init__(self):
            self.metadata = MockMetadata()
            self.mappers = []
        
        def add_mapper(self, name, module, table_name):
            self.mappers.append(MockMapper(name, module, table_name))
    
    class MockMetadata:
        def __init__(self):
            self.tables = {}
            self._bind = None
        
        def add_table(self, name, schema=None):
            self.tables[name] = MockTable(name, schema)
    
    registry = MockRegistry()
    registry.metadata.add_table("users")
    registry.metadata.add_table("orders")
    registry.add_mapper("User", "backend.models.user", "users")
    registry.add_mapper("Order", "backend.models.order", "orders")
    
    return registry
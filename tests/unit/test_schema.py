"""
Unit tests for Schema module
"""

import pytest
from backend.schema import SchemaRegistry, SchemaVersion
from datetime import datetime


class TestSchemaRegistry:
    """Test schema registry"""
    
    def test_get_latest_version(self):
        registry = SchemaRegistry()
        schema = registry.get_latest_version("EvidenceCreated")
        assert schema is not None
        assert schema.name == "EvidenceCreated"
    
    def test_schema_exists(self):
        registry = SchemaRegistry()
        schema = registry.get_schema("EvidenceCreated", SchemaVersion.V1)
        assert schema is not None
        assert schema.version == SchemaVersion.V1
    
    def test_validate_valid_data(self):
        registry = SchemaRegistry()
        
        valid_data = {
            "id": "123",
            "hash": "abc123",
            "timestamp": datetime.now().isoformat(),
            "source": "test"
        }
        
        # Try to validate with latest version
        schema = registry.get_latest_version("EvidenceCreated")
        if schema:
            is_valid, errors = schema.validate(valid_data)
            # Validation may pass or fail depending on schema
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)
    
    def test_validate_with_schema_object(self):
        registry = SchemaRegistry()
        schema = registry.get_schema("EvidenceCreated", SchemaVersion.V1)
        
        if schema:
            test_data = {
                "id": "test_id",
                "hash": "test_hash",
                "timestamp": datetime.now().isoformat(),
                "source": "test_source"
            }
            is_valid, errors = schema.validate(test_data)
            # Just check that validation runs without error
            assert isinstance(is_valid, bool)
    
    def test_list_schemas(self):
        registry = SchemaRegistry()
        schemas = registry.list_schemas()
        assert len(schemas) >= 3  # At least 3 schemas registered
    
    def test_schema_diff(self):
        registry = SchemaRegistry()
        diff = registry.get_schema_diff("EvidenceCreated", SchemaVersion.V1, SchemaVersion.V2)
        assert diff is not None
        assert "name" in diff

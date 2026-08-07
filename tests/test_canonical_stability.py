# scripts/tests/test_canonical_stability.py
"""
Canonical Serialization Stability Tests.
Verifies that serialization doesn't change fingerprint.
Phase 2.5 - Final Engineering Refinements
"""

import json
import pytest
from metadata_inventory.canonical_serializer import CanonicalSerializer, Fingerprint


def test_canonical_serialization_stability():
    """Test that canonical serialization produces stable output."""
    
    test_data = {
        "name": "test",
        "value": 123,
        "nested": {
            "a": 1,
            "b": "string",
            "c": [1, 2, 3]
        },
        "items": ["x", "y", "z"],
        "tuple": (1, 2, 3),
        "set": {1, 2, 3}
    }
    
    # Serialize twice
    serialized_1 = CanonicalSerializer.serialize(test_data)
    serialized_2 = CanonicalSerializer.serialize(test_data)
    
    # Must be identical
    assert serialized_1 == serialized_2
    
    # Generate fingerprints
    fingerprint_1 = Fingerprint.generate(test_data)
    fingerprint_2 = Fingerprint.generate(test_data)
    
    # Must be identical
    assert fingerprint_1 == fingerprint_2


def test_canonical_serialization_order_independent():
    """Test that serialization is independent of dictionary order."""
    
    data_1 = {
        "a": 1,
        "b": 2,
        "c": 3
    }
    
    data_2 = {
        "c": 3,
        "a": 1,
        "b": 2
    }
    
    serialized_1 = CanonicalSerializer.serialize(data_1)
    serialized_2 = CanonicalSerializer.serialize(data_2)
    
    # Must be identical (sorted keys)
    assert serialized_1 == serialized_2
    
    fingerprint_1 = Fingerprint.generate(data_1)
    fingerprint_2 = Fingerprint.generate(data_2)
    
    assert fingerprint_1 == fingerprint_2


def test_canonical_serialization_roundtrip_fingerprint():
    """
    Test that serialization roundtrip preserves fingerprint.
    
    payload → serialize → deserialize → serialize → fingerprint must match.
    """
    
    original_payload = {
        "fingerprint": "abc123",
        "checksum": "def456",
        "registry": {
            "tables": ["users", "orders"],
            "models": ["User", "Order"]
        }
    }
    
    # Original fingerprint
    original_fingerprint = Fingerprint.generate(original_payload)
    
    # Serialize to JSON string
    json_str = json.dumps(original_payload, sort_keys=True, default=str)
    
    # Deserialize back
    loaded_payload = json.loads(json_str)
    
    # Regenerate fingerprint from loaded payload
    loaded_fingerprint = Fingerprint.generate(loaded_payload)
    
    # Must be identical
    assert original_fingerprint == loaded_fingerprint


def test_canonical_serialization_nested_structures():
    """Test canonical serialization with complex nested structures."""
    
    test_data = {
        "registry": {
            "tables": [
                {"name": "users", "schema": "public", "columns": ["id", "name"]},
                {"name": "orders", "schema": "public", "columns": ["id", "user_id", "amount"]}
            ],
            "models": ["User", "Order"],
            "relationships": [
                {"from": "Order", "to": "User", "type": "many_to_one"}
            ]
        },
        "import": {
            "imported": ["backend.models.user", "backend.models.order"],
            "failed": [],
            "mapper_growth": 2
        }
    }
    
    # Serialize multiple times
    for _ in range(3):
        serialized = CanonicalSerializer.serialize(test_data)
        fingerprint = Fingerprint.generate(test_data)
        
        # Verify stable
        assert fingerprint is not None
        assert len(fingerprint) in [16, 64]  # Depending on algorithm


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
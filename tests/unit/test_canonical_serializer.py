# tests/unit/test_canonical_serializer.py
"""
Unit tests for Canonical Serializer.
"""

import pytest
from metadata_inventory.canonical_serializer import CanonicalSerializer, Fingerprint

pytestmark = pytest.mark.metadata_inventory


class TestCanonicalSerializer:
    """Test Canonical Serializer."""
    
    def test_serialize_dict(self):
        """Test serialization of dictionary."""
        data = {"a": 1, "b": 2}
        result = CanonicalSerializer.serialize(data)
        assert "a" in result
        assert "b" in result
    
    def test_serialize_list(self):
        """Test serialization of list."""
        data = [1, 2, 3]
        result = CanonicalSerializer.serialize(data)
        assert "[1,2,3]" in result
    
    def test_serialize_set(self):
        """Test serialization of set (sorted)."""
        data = {3, 1, 2}
        result = CanonicalSerializer.serialize(data)
        # Should be sorted
        assert result == "[1,2,3]"
    
    def test_order_independent(self):
        """Test serialization is order-independent."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}
        result1 = CanonicalSerializer.serialize(data1)
        result2 = CanonicalSerializer.serialize(data2)
        assert result1 == result2
    
    def test_fingerprint_generate(self):
        """Test fingerprint generation."""
        data = {"test": "value"}
        fp = Fingerprint.generate(data)
        assert len(fp) == 16
        assert isinstance(fp, str)
    
    def test_fingerprint_deterministic(self):
        """Test fingerprint is deterministic."""
        data = {"test": "value"}
        fp1 = Fingerprint.generate(data)
        fp2 = Fingerprint.generate(data)
        assert fp1 == fp2
    
    def test_fingerprint_different_data(self):
        """Test different data yields different fingerprint."""
        fp1 = Fingerprint.generate({"a": 1})
        fp2 = Fingerprint.generate({"b": 2})
        assert fp1 != fp2
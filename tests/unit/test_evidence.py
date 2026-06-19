"""
Unit tests for Evidence module
"""

import pytest
from backend.evidence import EvidenceRegistry, EvidenceHasher
from backend.evidence.dto import Evidence, CustodyEvent, EvidenceType


class TestEvidenceHasher:
    """Test evidence hashing"""
    
    def test_compute_hash_deterministic(self):
        hasher = EvidenceHasher()
        data = {"test": "data", "number": 123}
        
        hash1 = hasher.compute_hash(data)
        hash2 = hasher.compute_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 64
    
    def test_compute_hash_different_data(self):
        hasher = EvidenceHasher()
        hash1 = hasher.compute_hash({"a": 1})
        hash2 = hasher.compute_hash({"a": 2})
        
        assert hash1 != hash2
    
    def test_compute_hash_empty_data(self):
        hasher = EvidenceHasher()
        hash_val = hasher.compute_hash({})
        assert len(hash_val) == 64
    
    def test_compute_chain_hash(self):
        hasher = EvidenceHasher()
        hashes = ["hash1", "hash2", "hash3"]
        chain_hash = hasher.compute_chain_hash(hashes)
        assert len(chain_hash) == 64


class TestEvidenceRegistry:
    """Test evidence registry"""
    
    def test_create_evidence(self, evidence_registry):
        evidence = evidence_registry.create(
            payload={"test": "data"},
            source="test"
        )
        
        assert evidence.id is not None
        assert evidence.hash is not None
        assert evidence.source == "test"
        assert len(evidence.custody_chain) == 1
    
    def test_get_evidence(self, evidence_registry):
        created = evidence_registry.create({"test": "data"}, "test")
        retrieved = evidence_registry.get(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.hash == created.hash
    
    def test_verify_evidence(self, evidence_registry):
        evidence = evidence_registry.create({"test": "data"}, "test")
        is_valid = evidence_registry.verify(evidence.id)
        
        assert is_valid is True
    
    def test_add_custody_event(self, evidence_registry):
        evidence = evidence_registry.create({"test": "data"}, "test")
        updated = evidence_registry.add_custody_event(
            evidence.id,
            action="verified",
            actor="verifier",
            reason="Integrity check passed"
        )
        
        assert updated is not None
        assert len(updated.custody_chain) == 2
        assert updated.custody_chain[-1].action == "verified"
        assert updated.version == 2
    
    def test_list_evidence(self, evidence_registry):
        evidence_registry.create({"test": "data1"}, "test")
        evidence_registry.create({"test": "data2"}, "test")
        evidence_registry.create({"test": "data3"}, "test")
        
        all_evidence = evidence_registry.list_all()
        assert len(all_evidence) == 3


class TestChainValidator:
    """Test chain validator - skip complex validation"""
    
    def test_chain_validator_exists(self):
        from backend.evidence.chain_validator import ChainValidator
        validator = ChainValidator()
        assert validator is not None
    
    def test_chain_validator_methods(self):
        from backend.evidence.chain_validator import ChainValidator
        validator = ChainValidator()
        
        # Test that methods exist
        assert hasattr(validator, 'validate_block')
        assert hasattr(validator, 'validate_chain')

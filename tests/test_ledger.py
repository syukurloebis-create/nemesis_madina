# tests/test_ledger.py (FIXED)
import sys
import pytest
import hashlib  # ← TAMBAHKAN INI
from pathlib import Path

# Tambahkan scripts ke PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from metadata_inventory.append_ledger import AppendLedger, AppendRecord
from metadata_inventory.canonical_serializer import CanonicalSerializer
from metadata_inventory.contracts import ArtifactEnvelope, ArtifactId
from metadata_inventory.artifact_factory import ArtifactFactory


class TestLedgerIntegrity:
    """Tests for ledger integrity."""
    
    def test_append_only(self):
        """Ledger must be append-only."""
        ledger = AppendLedger()
        
        env1 = ArtifactEnvelope.create(
            name="test1",
            payload={"value": 1},
            producer="test",
            schema_version="1.0"
        )
        env2 = ArtifactEnvelope.create(
            name="test2",
            payload={"value": 2},
            producer="test",
            schema_version="1.0"
        )
        
        record1 = ledger.append(env1)
        record2 = ledger.append(env2)
        
        assert record1.sequence == 0
        assert record2.sequence == 1
        
        records = ledger.get_records()
        assert len(records) == 2
        assert records[0].artifact_id == env1.artifact_id.value
        assert records[1].artifact_id == env2.artifact_id.value
        
        # Duplicate append should return existing record
        record1_again = ledger.append(env1)
        assert record1_again.sequence == record1.sequence
        assert len(ledger.get_records()) == 2
    
    def test_hash_chain(self):
        """Ledger must maintain hash chain."""
        ledger = AppendLedger()
        
        env1 = ArtifactEnvelope.create(
            name="test1",
            payload={"value": 1},
            producer="test",
            schema_version="1.0"
        )
        env2 = ArtifactEnvelope.create(
            name="test2",
            payload={"value": 2},
            producer="test",
            schema_version="1.0"
        )
        
        record1 = ledger.append(env1)
        record2 = ledger.append(env2)
        
        assert record1.previous_hash == "0" * 16
        assert record2.previous_hash == record1.hash
        
        def verify_record(record):
            content = {
                "sequence": record.sequence,
                "artifact_id": record.artifact_id,
                "artifact_checksum": record.artifact_checksum,
                "timestamp": record.timestamp,
                "previous_hash": record.previous_hash,
                "metadata": record.metadata
            }
            canonical = CanonicalSerializer.serialize(content)
            expected = hashlib.sha256(canonical.encode()).hexdigest()[:16]  # ← hashlib tersedia
            return record.hash == expected
        
        assert verify_record(record1)
        assert verify_record(record2)
    
    def test_tamper_evident(self):
        """Ledger must be tamper-evident."""
        ledger = AppendLedger()
        
        env1 = ArtifactEnvelope.create(
            name="test1",
            payload={"value": 1},
            producer="test",
            schema_version="1.0"
        )
        env2 = ArtifactEnvelope.create(
            name="test2",
            payload={"value": 2},
            producer="test",
            schema_version="1.0"
        )
        
        ledger.append(env1)
        ledger.append(env2)
        
        assert ledger.verify() is True
    
    def test_merkle_root(self):
        """Ledger must provide Merkle root hash."""
        ledger = AppendLedger()
        
        for i in range(10):
            env = ArtifactEnvelope.create(
                name=f"test{i}",
                payload={"value": i},
                producer="test",
                schema_version="1.0"
            )
            ledger.append(env)
        
        root = ledger.get_root_hash()
        assert root is not None
        assert len(root) == 16
        
        root2 = ledger.get_root_hash()
        assert root == root2
        
        assert ledger.verify() is True
    
    def test_ledger_reproducible(self):
        """Ledger must be reproducible."""
        def create_ledger():
            ledger = AppendLedger()
            for i in range(5):
                env = ArtifactEnvelope.create(
                    name=f"test{i}",
                    payload={"value": i},
                    producer="test",
                    schema_version="1.0"
                )
                ledger.append(env)
            return ledger
        
        ledger1 = create_ledger()
        ledger2 = create_ledger()
        
        records1 = ledger1.get_records()
        records2 = ledger2.get_records()
        
        assert len(records1) == len(records2)
        for r1, r2 in zip(records1, records2):
            assert r1.sequence == r2.sequence
            assert r1.artifact_id == r2.artifact_id
            assert r1.hash == r2.hash
            assert r1.previous_hash == r2.previous_hash
        
        assert ledger1.get_root_hash() == ledger2.get_root_hash()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
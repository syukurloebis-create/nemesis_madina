"""Tests for chain validator"""

import pytest
from backend.evidence.chain_validator import ChainValidator


class TestChainValidator:
    def test_validate_valid_chain(self):
        validator = ChainValidator()
        chain = [{
            'index': 0,
            'previous_hash': '0',
            'timestamp': '2024-01-01T00:00:00',
            'data_hash': 'abc',
            'hash': 'abc'
        }]
        valid, errors = validator.validate_chain(chain)
        assert valid or len(errors) == 0
    
    def test_get_chain_metrics(self):
        validator = ChainValidator()
        metrics = validator.get_chain_metrics([])
        assert metrics['length'] == 0

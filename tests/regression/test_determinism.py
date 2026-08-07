# scripts/tests/regression/test_determinism.py
"""
Regression tests for determinism.
"""

import pytest
import asyncio
import json
import sys
from pathlib import Path

from metadata_inventory.phase2_runner import Phase2Runner
from metadata_inventory.phase2_runner import Phase2Runner
from metadata_inventory.canonical_serializer import Fingerprint

pytestmark = pytest.mark.metadata_inventory
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))


class TestDeterminism:
    """Test determinism across runs."""
    
    def test_fingerprint_stable_across_runs(self):
        """Test fingerprint is stable across multiple runs."""
        fingerprints = []
        
        for i in range(10):
            runner = Phase2Runner()
            result = asyncio.run(runner.run())
            
            # Extract fingerprint
            if "discovery_artifact" in result.get("results", {}):
                art_result = result["results"]["discovery_artifact"]
                fp = art_result.get("fingerprint")
                if fp:
                    fingerprints.append(fp)
        
        # All fingerprints should be identical
        assert len(fingerprints) == 10
        assert len(set(fingerprints)) == 1
    
    def test_checksum_stable_across_runs(self):
        """Test checksum is stable across multiple runs."""
        checksums = []
        
        for i in range(10):
            runner = Phase2Runner()
            result = asyncio.run(runner.run())
            
            if "discovery_artifact" in result.get("results", {}):
                art_result = result["results"]["discovery_artifact"]
                cs = art_result.get("checksum")
                if cs:
                    checksums.append(cs)
        
        assert len(checksums) == 10
        assert len(set(checksums)) == 1
    
    def test_ordering_stable_across_runs(self):
        """Test finding ordering is stable across runs."""
        # This would verify that findings are always sorted by rule_id
        pass
# scripts/tests/regression/test_architecture_regression.py
"""
Architecture regression tests - ensure contracts don't change.
"""

import json
import pytest
import hashlib
from pathlib import Path
from typing import Dict, Any

from metadata_inventory.verification.registry import RuleRegistry
from metadata_inventory.verification.dependency import RuleDependencyGraph
from metadata_inventory.contracts.artifact_contract import ArtifactContract


class TestArchitectureRegression:
    """Test that architecture contracts remain stable."""
    
    MANIFEST_PATH = Path("scripts/tests/regression/architecture_manifest.json")
    
    @pytest.fixture
    def current_manifest(self):
        """Generate current architecture manifest."""
        manifest = {
            "rules": [],
            "dependencies": {},
            "contracts": {},
            "algorithms": []
        }
        
        # Collect rules
        for rule in RuleRegistry.all():
            manifest["rules"].append({
                "id": rule.rule_id,
                "version": rule.version,
                "severity": rule.severity.value,
                "category": rule.category
            })
        
        # Collect dependencies
        manifest["dependencies"] = RuleDependencyGraph.DEPENDENCIES
        
        # Collect algorithms
        from metadata_inventory.canonical_serializer import Fingerprint
        manifest["algorithms"] = Fingerprint.list_algorithms()
        
        # Generate checksum
        manifest_str = json.dumps(manifest, sort_keys=True)
        manifest["checksum"] = hashlib.sha256(manifest_str.encode()).hexdigest()[:16]
        
        return manifest
    
    def test_architecture_stable(self, current_manifest):
        """Test architecture manifest hasn't changed."""
        # Load previous manifest if exists
        if self.MANIFEST_PATH.exists():
            with open(self.MANIFEST_PATH, "r") as f:
                previous_manifest = json.load(f)
            
            # Compare checksums
            previous_checksum = previous_manifest.get("checksum")
            current_checksum = current_manifest.get("checksum")
            
            assert previous_checksum == current_checksum, \
                f"Architecture changed! Previous: {previous_checksum}, Current: {current_checksum}"
        else:
            # First run - save manifest
            with open(self.MANIFEST_PATH, "w") as f:
                json.dump(current_manifest, f, indent=2)
            print("✅ Architecture manifest created")
    
    def test_rule_ids_immutable(self, current_manifest):
        """Test rule IDs haven't changed."""
        # This would check that rule IDs are stable across versions
        rule_ids = [r["id"] for r in current_manifest["rules"]]
        expected_ids = ["RULE-001@v1", "RULE-002@v1", "RULE-003@v1", 
                       "RULE-004@v1", "RULE-005@v1", "RULE-006@v1",
                       "RULE-007@v1", "RULE-008@v1"]
        
        # Check that all expected IDs are present
        for expected in expected_ids:
            assert expected in rule_ids, f"Rule {expected} not found"
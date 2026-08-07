# tests/rules/test_rule001_single_registry.py
"""
Test Rule 001: Single Canonical Registry.
"""

import pytest
from metadata_inventory.verification.rules import SingleCanonicalRegistryRule, Severity
from metadata_inventory.verification.registry import RuleRegistry

pytestmark = pytest.mark.metadata_inventory


class TestRule001:
    """Test single canonical registry rule."""
    
    def test_rule_exists(self):
        """Test rule exists in registry."""
        rule = RuleRegistry.get("RULE-001@v1")
        assert rule is not None
    
    def test_rule_metadata(self):
        """Test rule metadata."""
        rule = RuleRegistry.get("RULE-001@v1")
        assert rule.rule_id == "RULE-001@v1"
        assert rule.severity == Severity.CRITICAL
        assert rule.name == "Single Canonical Registry"
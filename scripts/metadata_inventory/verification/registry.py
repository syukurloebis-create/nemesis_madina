# scripts/metadata_inventory/verification/registry.py
"""
Immutable Rule Registry - Registry of all verification rules.
"""

from typing import Dict, List, Tuple, Optional, Any

from .rules import VerificationRule, Severity
from .rules import (
    SingleCanonicalRegistryRule,
    AllModelsHaveTablesRule,
    AllTablesHavePrimaryKeysRule,
)


class RuleRegistry:
    """Registry for verification rules."""
    
    _RULES: Dict[str, VerificationRule] = {}
    _RULE_LIST: Tuple[VerificationRule, ...] = ()
    
    @classmethod
    def _initialize(cls) -> None:
        """Initialize the registry."""
        if cls._RULES:
            return
        
        rules = [
            SingleCanonicalRegistryRule(),
            AllModelsHaveTablesRule(),
            AllTablesHavePrimaryKeysRule(),
        ]
        
        cls._RULES = {r.rule_id: r for r in rules}
        cls._RULE_LIST = tuple(rules)
    
    @classmethod
    def get(cls, rule_id: str) -> Optional[VerificationRule]:
        """Get a rule by ID."""
        cls._initialize()
        return cls._RULES.get(rule_id)
    
    @classmethod
    def all(cls) -> Tuple[VerificationRule, ...]:
        """Get all rules."""
        cls._initialize()
        return cls._RULE_LIST
    
    @classmethod
    def count(cls) -> int:
        """Get number of registered rules."""
        cls._initialize()
        return len(cls._RULE_LIST)
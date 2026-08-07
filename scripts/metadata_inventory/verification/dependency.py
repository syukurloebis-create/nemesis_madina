# scripts/metadata_inventory/verification/dependency.py
"""
Rule Dependency Graph - DAG for rule execution order.
Phase 3 - Production Hardening
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RuleDependency:
    """Dependency between rules."""
    rule_id: str
    depends_on: List[str]


class RuleDependencyGraph:
    """
    DAG for rule dependencies.
    Determines execution order and which rules to skip.
    """
    
    # Rule dependencies (immutable)
    DEPENDENCIES = {
        "RULE-001@v1": [],  # Single Canonical Registry - no deps
        "RULE-002@v1": ["RULE-001@v1"],  # Model Table - needs registry
        "RULE-003@v1": ["RULE-002@v1"],  # Table PK - needs tables
        "RULE-004@v1": [],  # Import Success - independent
        "RULE-005@v1": [],  # Checksum Integrity - independent
        "RULE-006@v1": [],  # Identity Stability - independent
        "RULE-007@v1": ["RULE-002@v1"],  # Mapper Duplicate - needs models
        "RULE-008@v1": ["RULE-002@v1", "RULE-003@v1"],  # FK Integrity - needs tables
    }
    
    @classmethod
    def get_order(cls) -> List[str]:
        """Get topological execution order."""
        visited = set()
        order = []
        
        def dfs(rule_id: str):
            if rule_id in visited:
                return
            visited.add(rule_id)
            for dep in cls.DEPENDENCIES.get(rule_id, []):
                dfs(dep)
            order.append(rule_id)
        
        for rule_id in cls.DEPENDENCIES:
            dfs(rule_id)
        
        return order
    
    @classmethod
    def get_dependencies(cls, rule_id: str) -> List[str]:
        """Get dependencies of a rule."""
        return cls.DEPENDENCIES.get(rule_id, [])
    
    @classmethod
    def can_skip(cls, rule_id: str, failed_rules: Set[str]) -> bool:
        """Check if rule can be skipped due to failed dependencies."""
        for dep in cls.DEPENDENCIES.get(rule_id, []):
            if dep in failed_rules:
                return True
        return False
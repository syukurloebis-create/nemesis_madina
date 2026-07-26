# scripts/rules/versioned_rule.py
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class VersionedRule:
    """Immutable versioned rule"""
    id: str
    name: str
    version: int
    category: str
    severity: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    created_at: datetime
    deprecated: bool = False
    superseded_by: Optional[str] = None
    changelog: Optional[str] = None

class RuleVersionManager:
    """Manage rule versions"""
    
    def __init__(self, rule_graph: RuleGraph):
        self.rule_graph = rule_graph
        self._rules: Dict[str, List[VersionedRule]] = {}
    
    def add_rule(self, rule: VersionedRule):
        """Add a new rule version"""
        if rule.id not in self._rules:
            self._rules[rule.id] = []
        self._rules[rule.id].append(rule)
        self.rule_graph.add_rule(self._create_rule_node(rule))
    
    def get_rule(self, rule_id: str, version: Optional[int] = None) -> Optional[VersionedRule]:
        """Get rule by ID and optional version"""
        if rule_id not in self._rules:
            return None
        
        versions = self._rules[rule_id]
        if version is None:
            # Return latest non-deprecated version
            for v in reversed(versions):
                if not v.deprecated:
                    return v
            return versions[-1] if versions else None
        
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def deprecate_rule(self, rule_id: str, version: int, superseded_by: Optional[str] = None):
        """Deprecate a specific rule version"""
        versions = self._rules.get(rule_id, [])
        for v in versions:
            if v.version == version:
                v.deprecated = True
                v.superseded_by = superseded_by
                return
        raise ValueError(f"Rule version {version} not found")
    
    def get_execution_plan(self, rule_ids: List[str] = None) -> List[str]:
        """Get execution plan for specific rules"""
        if rule_ids is None:
            rule_ids = list(self._rules.keys())
        
        # Get latest version for each rule
        rules = [self.get_rule(rid) for rid in rule_ids if self.get_rule(rid)]
        rule_nodes = [self._create_rule_node(r) for r in rules if r]
        
        # Add to graph
        for node in rule_nodes:
            self.rule_graph.add_rule(node)
        
        return self.rule_graph.get_execution_order()
# scripts/rules/graph.py
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

@dataclass
class RuleNode:
    """Node in rule dependency graph"""
    id: str
    name: str
    category: str
    depends_on: List[str] = None
    rule: Any = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []

class RuleGraph:
    """Directed Acyclic Graph of rules"""
    
    def __init__(self):
        self.nodes: Dict[str, RuleNode] = {}
        self.edges: Dict[str, Set[str]] = {}
    
    def add_rule(self, rule: RuleNode):
        """Add a rule to the graph"""
        self.nodes[rule.id] = rule
        self.edges[rule.id] = set(rule.depends_on)
    
    def get_dependencies(self, rule_id: str) -> List[str]:
        """Get all dependencies of a rule (recursive)"""
        result = []
        visited = set()
        
        def traverse(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            for dep in self.edges.get(node_id, []):
                result.append(dep)
                traverse(dep)
        
        traverse(rule_id)
        return result
    
    def get_dependents(self, rule_id: str) -> List[str]:
        """Get all rules that depend on this rule"""
        result = []
        for node_id, deps in self.edges.items():
            if rule_id in deps:
                result.append(node_id)
        return result
    
    def get_execution_order(self) -> List[str]:
        """Get topological execution order"""
        # Kahn's algorithm for topological sort
        in_degree = {node: 0 for node in self.nodes}
        for node_id, deps in self.edges.items():
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0) + 1
        
        queue = [n for n in self.nodes if in_degree.get(n, 0) == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            for dep in self.edges.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        
        if len(result) != len(self.nodes):
            raise ValueError("Circular dependency detected in rule graph")
        
        return result
    
    def validate(self) -> List[str]:
        """Validate graph for cycles and missing dependencies"""
        errors = []
        
        # Check for missing dependencies
        for node_id, deps in self.edges.items():
            for dep in deps:
                if dep not in self.nodes:
                    errors.append(f"Missing dependency: {dep} -> {node_id}")
        
        # Check for cycles (try to detect)
        try:
            self.get_execution_order()
        except ValueError as e:
            errors.append(str(e))
        
        return errors
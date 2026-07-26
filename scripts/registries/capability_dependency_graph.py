# scripts/registries/capability_dependency_graph.py
import networkx as nx
from typing import Dict, List, Set, Any

class CapabilityDependencyGraph:
    """Dependency graph for capabilities"""
    
    def __init__(self, capability_registry: IRegistry):
        self.registry = capability_registry
        self.graph = nx.DiGraph()
        self._build_graph()
    
    def _build_graph(self):
        """Build dependency graph from registry"""
        capabilities = self.registry.list()
        
        for cap in capabilities:
            self.graph.add_node(cap['id'], **cap)
            for dep in cap.get('depends_on', []):
                self.graph.add_edge(cap['id'], dep)
    
    def get_dependencies(self, capability_id: str) -> List[str]:
        """Get all direct dependencies"""
        return list(self.graph.successors(capability_id))
    
    def get_dependents(self, capability_id: str) -> List[str]:
        """Get all direct dependents"""
        return list(self.graph.predecessors(capability_id))
    
    def get_all_dependencies(self, capability_id: str) -> Set[str]:
        """Get all transitive dependencies (recursive)"""
        result = set()
        def traverse(node):
            for dep in self.graph.successors(node):
                result.add(dep)
                traverse(dep)
        traverse(capability_id)
        return result
    
    def get_all_dependents(self, capability_id: str) -> Set[str]:
        """Get all transitive dependents (recursive)"""
        result = set()
        def traverse(node):
            for dep in self.graph.predecessors(node):
                result.add(dep)
                traverse(dep)
        traverse(capability_id)
        return result
    
    def get_impact_analysis(self, capability_id: str) -> Dict[str, Any]:
        """Get full impact analysis for a capability"""
        return {
            'capability': capability_id,
            'direct_dependencies': self.get_dependencies(capability_id),
            'all_dependencies': self.get_all_dependencies(capability_id),
            'direct_dependents': self.get_dependents(capability_id),
            'all_dependents': self.get_all_dependents(capability_id),
            'blast_radius': len(self.get_all_dependents(capability_id)),
            'is_critical': len(self.get_all_dependents(capability_id)) > 10
        }
    
    def find_critical_path(self) -> List[str]:
        """Find the critical path (longest dependency chain)"""
        # Find longest path in DAG
        # TODO: Implement using networkx
        pass
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies"""
        cycles = []
        try:
            cycles = list(nx.simple_cycles(self.graph))
        except nx.NetworkXNoCycle:
            pass
        return cycles
"""
Execution Plan - Immutable execution plan.
Phase 1 - Core Infrastructure
"""

from typing import Dict, List, Optional, Any, Callable, Type, Set
from dataclasses import dataclass, field

from .contracts import NodeDefinition, Dependency, DependencyType
from .canonical_serializer import Fingerprint


@dataclass(frozen=True)
class ExecutionPlan:
    """Immutable execution plan."""
    plan_id: str
    topology_hash: str
    node_order: List[str]
    groups: List[List[str]]
    checksum: str
    node_count: int
    dependency_count: int


class ExecutionPlanner:
    """Execution planner that produces immutable plans."""
    
    def __init__(self, nodes: Dict[str, NodeDefinition]):
        self._nodes = nodes
        self._plan: Optional[ExecutionPlan] = None
    
    def plan(self) -> ExecutionPlan:
        """Generate immutable execution plan."""
        if self._plan is not None:
            return self._plan
        
        # Calculate topology hash
        topology = {
            name: {
                "depends_on": [dep.node_name for dep in node.depends_on],
                "type": node.output_type.__name__
            }
            for name, node in self._nodes.items()
        }
        topology_hash = Fingerprint.generate(topology)
        
        # Get execution groups
        groups = self._get_execution_groups()
        
        # Flatten groups for node order
        node_order = []
        for group in groups:
            node_order.extend(sorted(group))
        
        # Create plan content
        plan_content = {
            "topology_hash": topology_hash,
            "groups": groups,
            "node_order": node_order
        }
        plan_id = Fingerprint.generate(plan_content)
        checksum = Fingerprint.generate({
            **plan_content,
            "created_at": "2026-01-01T00:00:00Z"
        })
        
        self._plan = ExecutionPlan(
            plan_id=plan_id,
            topology_hash=topology_hash,
            node_order=node_order,
            groups=groups,
            checksum=checksum,
            node_count=len(self._nodes),
            dependency_count=sum(len(node.depends_on) for node in self._nodes.values())
        )
        
        return self._plan
    
    def _get_execution_groups(self) -> List[List[str]]:
        """Get parallel execution groups (deterministic)."""
        in_degree = {name: 0 for name in self._nodes}
        for name, node in self._nodes.items():
            for dep in node.depends_on:
                if dep.dependency_type != DependencyType.OPTIONAL:
                    in_degree[name] += 1
        
        queue = sorted([name for name, degree in in_degree.items() if degree == 0])
        groups = []
        processed = set()
        
        while queue:
            group = sorted(queue)
            groups.append(group)
            processed.update(group)
            
            next_queue = []
            for name in sorted(self._nodes.keys()):
                if name in processed:
                    continue
                for dep in self._nodes[name].depends_on:
                    if dep.node_name in processed and dep.dependency_type != DependencyType.OPTIONAL:
                        in_degree[name] -= 1
                        if in_degree[name] == 0:
                            next_queue.append(name)
            
            queue = sorted(set(next_queue))
        
        remaining = sorted(set(self._nodes.keys()) - processed)
        if remaining:
            groups.append(remaining)
        
        return groups
    
    def get_plan(self) -> Optional[ExecutionPlan]:
        return self._plan
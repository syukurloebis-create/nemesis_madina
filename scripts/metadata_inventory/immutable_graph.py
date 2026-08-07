# immutable_graph.py
"""
Immutable Graph Snapshot - Fully immutable DAG representation.
Phase 1.7 - Runtime Determinism & Contract Completeness
"""

from typing import Dict, List, Set, Tuple, Optional, Any, FrozenSet, Callable, Type
from dataclasses import dataclass, field
from types import MappingProxyType

from contracts import NodeDefinition, Dependency, DependencyType


@dataclass(frozen=True)
class ImmutableNodeDefinition:
    """Immutable node definition with frozen collections."""
    name: str
    engine: str
    depends_on: Tuple[str, ...]  # Only node names, not full Dependency objects
    dependency_types: Tuple[Tuple[str, DependencyType], ...]  # (node_name, type)
    input_types: MappingProxyType  # name -> type name
    output_type: str
    max_retries: int
    timeout_seconds: float
    retry_policy: str
    
    @classmethod
    def from_node_definition(cls, node: NodeDefinition) -> 'ImmutableNodeDefinition':
        """Create immutable version from mutable node definition."""
        # Convert depends_on to tuples
        depends_on = tuple(d.node_name for d in node.depends_on)
        dependency_types = tuple(
            (d.node_name, d.dependency_type) for d in node.depends_on
        )
        
        # Convert input_types to MappingProxyType
        input_types = MappingProxyType({
            k: v.__name__ for k, v in node.input_types.items()
        })
        
        return cls(
            name=node.name,
            engine=node.engine,
            depends_on=depends_on,
            dependency_types=dependency_types,
            input_types=input_types,
            output_type=node.output_type.__name__,
            max_retries=node.max_retries,
            timeout_seconds=node.timeout_seconds,
            retry_policy=node.retry_policy
        )


@dataclass(frozen=True)
class ImmutableGraphSnapshot:
    """
    Fully immutable graph snapshot.
    All collections are immutable (tuples, frozen sets, mapping proxy).
    """
    nodes: MappingProxyType  # name -> ImmutableNodeDefinition
    node_names: Tuple[str, ...]
    topology_hash: str
    plan_checksum: str
    created_at: str
    
    @classmethod
    def from_nodes(cls, nodes: Dict[str, NodeDefinition]) -> 'ImmutableGraphSnapshot':
        """Create immutable snapshot from mutable nodes."""
        from canonical_serializer import Fingerprint
        from datetime import datetime
        
        # Create immutable nodes
        immutable_nodes = {
            name: ImmutableNodeDefinition.from_node_definition(node)
            for name, node in nodes.items()
        }
        
        # Create mapping proxy
        nodes_proxy = MappingProxyType(immutable_nodes)
        
        # Get sorted node names
        node_names = tuple(sorted(nodes.keys()))
        
        # Calculate topology hash
        topology = {
            name: {
                "depends_on": list(node.depends_on),
                "output_type": node.output_type,
                "engine": node.engine
            }
            for name, node in immutable_nodes.items()
        }
        topology_hash = Fingerprint.generate(topology)
        
        # Calculate plan checksum
        plan_content = {
            "topology_hash": topology_hash,
            "node_names": node_names,
            "nodes": {
                name: {
                    "depends_on": node.depends_on,
                    "output_type": node.output_type
                }
                for name, node in immutable_nodes.items()
            }
        }
        plan_checksum = Fingerprint.generate(plan_content)
        
        return cls(
            nodes=nodes_proxy,
            node_names=node_names,
            topology_hash=topology_hash,
            plan_checksum=plan_checksum,
            created_at=datetime.now().isoformat()
        )
    
    def get_node(self, name: str) -> Optional[ImmutableNodeDefinition]:
        """Get node by name."""
        return self.nodes.get(name)
    
    def get_dependencies(self, name: str) -> Tuple[str, ...]:
        """Get dependencies of a node."""
        node = self.get_node(name)
        return node.depends_on if node else ()
    
    def get_dependency_type(self, name: str, dep_name: str) -> Optional[DependencyType]:
        """Get dependency type between nodes."""
        node = self.get_node(name)
        if not node:
            return None
        for dep, dep_type in node.dependency_types:
            if dep == dep_name:
                return dep_type
        return None
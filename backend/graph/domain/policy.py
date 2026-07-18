"""
Graph Domain - Policy

Business policy for graph operations.
"""

from abc import ABC, abstractmethod
from typing import List

from backend.graph.domain.aggregate import GraphAggregate


class GraphPolicy(ABC):
    """
    Graph Policy - Domain Service.
    
    Enforces business policies on graph aggregates.
    Policies are business rules that may span multiple aggregates.
    """
    
    @abstractmethod
    def validate(self, aggregate: GraphAggregate) -> None:
        """Validate aggregate against policy."""
        pass


class NoVendorSelfReferencePolicy(GraphPolicy):
    """Policy: Vendor cannot be related to itself."""
    
    def validate(self, aggregate: GraphAggregate) -> None:
        for edge in aggregate.edges:
            if edge.source_key == edge.target_key:
                raise ValueError(f"Vendor self-reference: {edge.source_key}")


class NoDuplicateVendorPolicy(GraphPolicy):
    """Policy: No duplicate vendors."""
    
    def validate(self, aggregate: GraphAggregate) -> None:
        seen = set()
        for node in aggregate.nodes:
            if node.entity_type == "vendor":
                if node.business_key in seen:
                    raise ValueError(f"Duplicate vendor: {node.business_key}")
                seen.add(node.business_key)


class PolicyRegistry:
    """Registry for graph policies."""
    
    def __init__(self):
        self._policies: dict = {}
    
    def register(self, name: str, policy: GraphPolicy) -> None:
        """Register a policy."""
        self._policies[name] = policy
    
    def get(self, name: str) -> GraphPolicy:
        """Get a policy by name."""
        return self._policies[name]
    
    def validate_all(self, aggregate: GraphAggregate) -> None:
        """Validate aggregate against all policies."""
        for policy in self._policies.values():
            policy.validate(aggregate)
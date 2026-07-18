"""
Graph Domain - Validators

Domain validators for syntax, semantic, and business validation.
"""

from typing import List, Optional

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate


class SyntaxValidator:
    """
    Syntax Validator - validates format and structure.
    
    Examples:
    - NPWP format: 99.999.999.9-999.999
    - Package code format: XX-YYYY-ZZZZ
    - Email format: user@domain.com
    """
    
    @staticmethod
    def validate_vendor(node: GraphNode) -> None:
        """Validate vendor node syntax."""
        if not node.business_key:
            raise ValueError("Vendor business_key is required")
        if len(node.business_key) < 5:
            raise ValueError("Vendor business_key too short")
        # NPWP format validation can be added here
    
    @staticmethod
    def validate_package(node: GraphNode) -> None:
        """Validate package node syntax."""
        if not node.business_key:
            raise ValueError("Package business_key is required")
        # Package code format validation
    
    @staticmethod
    def validate_officer(node: GraphNode) -> None:
        """Validate officer node syntax."""
        if not node.business_key:
            raise ValueError("Officer business_key is required")
        # NIP format validation


class SemanticValidator:
    """
    Semantic Validator - validates existence and validity.
    
    Examples:
    - Vendor exists in system
    - Package exists in system
    - Officer exists in system
    """
    
    @staticmethod
    def validate_vendor_exists(business_key: str) -> None:
        """Validate vendor exists."""
        # This may require infrastructure access
        # In Domain, we just check format
        if not business_key:
            raise ValueError("Vendor key is required")
    
    @staticmethod
    def validate_edge_semantic(edge: GraphEdge, nodes: List[GraphNode]) -> None:
        """Validate edge semantics."""
        # Check that source and target are compatible
        source_nodes = [n for n in nodes if n.business_key == edge.source_key]
        target_nodes = [n for n in nodes if n.business_key == edge.target_key]
        
        if not source_nodes:
            raise ValueError(f"Source node not found: {edge.source_key}")
        if not target_nodes:
            raise ValueError(f"Target node not found: {edge.target_key}")


class BusinessValidator:
    """
    Business Validator - validates business rules.
    
    Examples:
    - Vendor cannot be related to itself
    - Officer cannot approve own packages
    - Package cannot have multiple winners
    """
    
    @staticmethod
    def validate_no_self_reference(aggregate: GraphAggregate) -> None:
        """Business rule: No self-references."""
        for edge in aggregate.edges:
            if edge.source_key == edge.target_key:
                raise ValueError(f"Self-reference: {edge.source_key}")
    
    @staticmethod
    def validate_no_duplicate_business_keys(aggregate: GraphAggregate) -> None:
        """Business rule: No duplicate business keys."""
        seen = set()
        for node in aggregate.nodes:
            if node.business_key in seen:
                raise ValueError(f"Duplicate business key: {node.business_key}")
            seen.add(node.business_key)
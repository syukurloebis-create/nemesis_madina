"""
Graph Builder - Domain Service.

Builds GraphAggregate from source data.
No persistence - only builds domain objects.
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge


class GraphBuilder:
    """
    Builds GraphAggregate from source data.
    
    Responsibilities:
    - Build GraphAggregate from source data
    - Use Business Keys (not database IDs)
    - Validate source data structure
    
    Does NOT:
    - Persist data
    - Enforce database invariants (handled by aggregate)
    - Orchestrate regeneration (handled by service)
    """
    
    def build(
        self,
        case_id: UUID,
        institution_id: UUID,
        source_data: Dict[str, Any],
    ) -> GraphAggregate:
        """
        Build GraphAggregate from source data.
        
        Args:
            case_id: Case UUID
            institution_id: Institution UUID
            source_data: Source data (RUP, packages, vendors)
            
        Returns:
            GraphAggregate domain model
            
        Raises:
            ValueError: If source_data is invalid
        """
        # Extract nodes and edges from source data
        nodes = self._build_nodes(source_data)
        edges = self._build_edges(source_data, nodes)
        
        return GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=tuple(nodes),
            edges=tuple(edges),
        )
    
    def _build_nodes(self, source_data: Dict[str, Any]) -> List[GraphNode]:
        """
        Build GraphNode objects from source data.
        
        Args:
            source_data: Source data dictionary
            
        Returns:
            List of GraphNode objects
        """
        nodes = []
        
        # Extract vendors
        vendors = source_data.get("vendors", [])
        for vendor in vendors:
            node = GraphNode(
                business_key=vendor.get("npwp") or vendor.get("code"),
                entity_type="vendor",
                name=vendor.get("name"),
                confidence=vendor.get("confidence", 0.5),
                risk_score=vendor.get("risk_score", 0.0),
                extra_data=vendor.get("extra_data", {}),
            )
            nodes.append(node)
        
        # Extract packages
        packages = source_data.get("packages", [])
        for package in packages:
            node = GraphNode(
                business_key=package.get("package_code") or package.get("id"),
                entity_type="package",
                name=package.get("name"),
                confidence=package.get("confidence", 0.5),
                risk_score=package.get("risk_score", 0.0),
                extra_data=package.get("extra_data", {}),
            )
            nodes.append(node)
        
        # Extract institutions
        institutions = source_data.get("institutions", [])
        for institution in institutions:
            node = GraphNode(
                business_key=institution.get("id"),
                entity_type="institution",
                name=institution.get("name"),
                confidence=institution.get("confidence", 0.5),
                risk_score=institution.get("risk_score", 0.0),
                extra_data=institution.get("extra_data", {}),
            )
            nodes.append(node)
        
        return nodes
    
    def _build_edges(
        self,
        source_data: Dict[str, Any],
        nodes: List[GraphNode],
    ) -> List[GraphEdge]:
        """
        Build GraphEdge objects from source data.
        
        Args:
            source_data: Source data dictionary
            nodes: Existing GraphNode objects
            
        Returns:
            List of GraphEdge objects
        """
        edges = []
        node_keys = {n.business_key for n in nodes}
        
        # Extract relationships
        relationships = source_data.get("relationships", [])
        for rel in relationships:
            source_key = rel.get("source")
            target_key = rel.get("target")
            
            # Skip if source or target not found
            if source_key not in node_keys or target_key not in node_keys:
                continue
            
            edge = GraphEdge(
                source_key=source_key,
                target_key=target_key,
                relationship_type=rel.get("relationship_type", "VENDOR_COLLUSION"),
                weight=rel.get("weight", 1.0),
                amount=rel.get("amount"),
                description=rel.get("description"),
                extra_data=rel.get("extra_data", {}),
            )
            edges.append(edge)
        
        return edges
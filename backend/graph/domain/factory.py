"""
Graph Domain - Factories
"""

from typing import Dict, Any, List, Optional
from uuid import UUID

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate


class GraphNodeFactory:
    """Factory for creating GraphNode instances."""
    
    @staticmethod
    def create_vendor(data: Dict[str, Any]) -> GraphNode:
        """Create a vendor node from dict data."""
        return GraphNode(
            business_key=data.get("npwp"),
            entity_type="vendor",
            name=data.get("name"),
            extra_data={
                "address": data.get("address"),
                "sector": data.get("sector"),
                "registration_date": data.get("registration_date"),
                **data.get("extra_data", {}),
            },
        )
    
    @staticmethod
    def create_package(data: Dict[str, Any]) -> GraphNode:
        """Create a package node from dict data."""
        return GraphNode(
            business_key=data.get("package_code"),
            entity_type="package",
            name=data.get("name"),
            extra_data={
                "value": data.get("value"),
                "procuring_institution": data.get("procuring_institution"),
                "procurement_method": data.get("procurement_method"),
                **data.get("extra_data", {}),
            },
        )
    
    @staticmethod
    def create_officer(data: Dict[str, Any]) -> GraphNode:
        """Create an officer node from dict data."""
        return GraphNode(
            business_key=data.get("nip"),
            entity_type="officer",
            name=data.get("name"),
            extra_data={
                "position": data.get("position"),
                "institution": data.get("institution"),
                **data.get("extra_data", {}),
            },
        )
    
    @staticmethod
    def create_institution(data: Dict[str, Any]) -> GraphNode:
        """Create an institution node from dict data."""
        return GraphNode(
            business_key=data.get("id"),
            entity_type="institution",
            name=data.get("name"),
            extra_data={
                "type": data.get("type"),
                "address": data.get("address"),
                **data.get("extra_data", {}),
            },
        )


class GraphEdgeFactory:
    """Factory for creating GraphEdge instances."""
    
    @staticmethod
    def create_collusion_edge(source: str, target: str, data: Dict[str, Any]) -> GraphEdge:
        """Create a collusion edge."""
        return GraphEdge(
            source_key=source,
            target_key=target,
            relationship_type="COLLUSION",
            weight=data.get("weight", 1.0),
            amount=data.get("amount"),
            description=data.get("description"),
            extra_data=data.get("extra_data", {}),
        )
    
    @staticmethod
    def create_contract_edge(source: str, target: str, data: Dict[str, Any]) -> GraphEdge:
        """Create a contract edge."""
        return GraphEdge(
            source_key=source,
            target_key=target,
            relationship_type="CONTRACT",
            weight=data.get("weight", 1.0),
            amount=data.get("amount"),
            description=data.get("description"),
            extra_data=data.get("extra_data", {}),
        )
    
    @staticmethod
    def create_ownership_edge(source: str, target: str, data: Dict[str, Any]) -> GraphEdge:
        """Create an ownership edge."""
        return GraphEdge(
            source_key=source,
            target_key=target,
            relationship_type="OWNERSHIP",
            weight=data.get("weight", 1.0),
            amount=data.get("percentage"),
            description=data.get("description"),
            extra_data=data.get("extra_data", {}),
        )


class GraphAggregateFactory:
    """Factory for creating GraphAggregate instances."""
    
    @staticmethod
    def create(
        case_id: UUID,
        institution_id: UUID,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        version: int = 1,
        checksum: Optional[str] = None,
    ) -> GraphAggregate:
        """Create a GraphAggregate."""
        return GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=tuple(nodes),
            edges=tuple(edges),
            version=version,
            checksum=checksum,
        )
    
    @staticmethod
    def rehydrate(
        case_id: UUID,
        institution_id: UUID,
        nodes: List[GraphNode],
        edges: List[GraphEdge],
        version: int,
        checksum: str,
    ) -> GraphAggregate:
        """Rehydrate an aggregate from persistence."""
        return GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=tuple(nodes),
            edges=tuple(edges),
            version=version,
            checksum=checksum,
        )
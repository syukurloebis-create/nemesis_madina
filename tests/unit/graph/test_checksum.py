"""
Unit Tests - GraphChecksumService
"""

import pytest
from uuid import uuid4

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.checksum import GraphChecksumService


class TestGraphChecksumService:
    """Tests for GraphChecksumService."""
    
    def test_compute_checksum(self):
        """Compute checksum from aggregate."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        service = GraphChecksumService()
        checksum = service.compute(aggregate)
        
        assert len(checksum) == 64  # SHA-256
        assert isinstance(checksum, str)
    
    def test_checksum_deterministic(self):
        """Checksum must be deterministic."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate1 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        aggregate2 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        service = GraphChecksumService()
        checksum1 = service.compute(aggregate1)
        checksum2 = service.compute(aggregate2)
        
        assert checksum1 == checksum2
    
    def test_checksum_order_independent(self):
        """Checksum should be independent of node/edge order."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge1 = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate1 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge1,),
        )
        
        aggregate2 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node2, node1),  # Reversed order
            edges=(edge1,),
        )
        
        service = GraphChecksumService()
        checksum1 = service.compute(aggregate1)
        checksum2 = service.compute(aggregate2)
        
        assert checksum1 == checksum2
    
    def test_checksum_changes_with_data(self):
        """Checksum changes when data changes."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        
        aggregate1 = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(edge,),
        )
        
        node3 = GraphNode("vendor_003", "vendor", "PT C")
        aggregate2 = aggregate1.add_node(node3)
        
        service = GraphChecksumService()
        checksum1 = service.compute(aggregate1)
        checksum2 = service.compute(aggregate2)
        
        assert checksum1 != checksum2
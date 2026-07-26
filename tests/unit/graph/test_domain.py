"""
Unit Tests - Graph Domain Models
"""

import pytest
from uuid import uuid4

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate, BusinessInvariantViolation


class TestGraphNode:
    """Tests for GraphNode value object."""
    
    def test_create_valid_node(self):
        """Create a valid node."""
        node = GraphNode(
            business_key="vendor_001",
            entity_type="vendor",
            name="PT Maju Jaya",
        )
        assert node.business_key == "vendor_001"
        assert node.entity_type == "vendor"
        assert node.name == "PT Maju Jaya"
    
    def test_node_requires_business_key(self):
        """Node must have a business key."""
        with pytest.raises(ValueError, match="business_key is required"):
            GraphNode(business_key="", entity_type="vendor", name="Test")
    
    def test_node_requires_entity_type(self):
        """Node must have an entity type."""
        with pytest.raises(ValueError, match="entity_type is required"):
            GraphNode(business_key="test", entity_type="", name="Test")
    
    def test_node_requires_name(self):
        """Node must have a name."""
        with pytest.raises(ValueError, match="name is required"):
            GraphNode(business_key="test", entity_type="vendor", name="")


class TestGraphEdge:
    """Tests for GraphEdge value object."""
    
    def test_create_valid_edge(self):
        """Create a valid edge."""
        edge = GraphEdge(
            source_key="vendor_001",
            target_key="vendor_002",
            relationship_type="COLLUSION",
            weight=0.8,
            amount=1000000,
        )
        assert edge.source_key == "vendor_001"
        assert edge.target_key == "vendor_002"
        assert edge.relationship_type == "COLLUSION"
        assert edge.weight == 0.8
        assert edge.amount == 1000000
    
    def test_edge_requires_source_key(self):
        """Edge must have a source key."""
        with pytest.raises(ValueError, match="source_key is required"):
            GraphEdge(source_key="", target_key="test", relationship_type="COLLUSION")
    
    def test_edge_requires_target_key(self):
        """Edge must have a target key."""
        with pytest.raises(ValueError, match="target_key is required"):
            GraphEdge(source_key="test", target_key="", relationship_type="COLLUSION")
    
    def test_edge_prohibits_self_loop(self):
        """Self-loops are prohibited."""
        with pytest.raises(ValueError, match="Self-loop is prohibited"):
            GraphEdge(
                source_key="vendor_001",
                target_key="vendor_001",
                relationship_type="COLLUSION",
            )
    
    def test_edge_requires_valid_weight(self):
        """Weight must be between 0 and 1."""
        with pytest.raises(ValueError, match="weight must be between"):
            GraphEdge(
                source_key="a", target_key="b",
                relationship_type="TEST",
                weight=1.5,
            )
        with pytest.raises(ValueError, match="weight must be between"):
            GraphEdge(
                source_key="a", target_key="b",
                relationship_type="TEST",
                weight=-0.5,
            )


class TestGraphAggregate:
    """Tests for GraphAggregate aggregate root."""
    
    def test_create_valid_aggregate(self):
        """Create a valid aggregate."""
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
        
        assert aggregate.case_id == case_id
        assert aggregate.institution_id == institution_id
        assert aggregate.node_count == 2
        assert aggregate.edge_count == 1
    
    def test_aggregate_prohibits_duplicate_nodes(self):
        """Duplicate nodes are prohibited."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_001", "vendor", "PT A")  # Same business_key
        
        with pytest.raises(BusinessInvariantViolation, match="Duplicate node"):
            GraphAggregate(
                case_id=case_id,
                institution_id=institution_id,
                nodes=(node1, node2),
                edges=(),
            )
    
    def test_aggregate_prohibits_duplicate_edges(self):
        """Duplicate edges are prohibited."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge1 = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        edge2 = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.9)
        
        with pytest.raises(BusinessInvariantViolation, match="Duplicate edge"):
            GraphAggregate(
                case_id=case_id,
                institution_id=institution_id,
                nodes=(node1, node2),
                edges=(edge1, edge2),
            )
    
    def test_aggregate_prohibits_orphan_edges(self):
        """Orphan edges are prohibited."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        edge = GraphEdge("vendor_003", "vendor_002", "COLLUSION", 0.8)  # source not exists
        
        with pytest.raises(BusinessInvariantViolation, match="Orphan edge"):
            GraphAggregate(
                case_id=case_id,
                institution_id=institution_id,
                nodes=(node1, node2),
                edges=(edge,),
            )
    
    def test_aggregate_add_node(self):
        """Adding a node returns a new aggregate."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1,),
            edges=(),
        )
        
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        new_aggregate = aggregate.add_node(node2)
        
        assert new_aggregate is not aggregate
        assert new_aggregate.node_count == 2
        assert new_aggregate.version == 2
    
    def test_aggregate_add_edge(self):
        """Adding an edge returns a new aggregate."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        node2 = GraphNode("vendor_002", "vendor", "PT B")
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1, node2),
            edges=(),
        )
        
        edge = GraphEdge("vendor_001", "vendor_002", "COLLUSION", 0.8)
        new_aggregate = aggregate.add_edge(edge)
        
        assert new_aggregate is not aggregate
        assert new_aggregate.edge_count == 1
        assert new_aggregate.version == 2
    
    def test_aggregate_contains_node(self):
        """Check if node exists."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1,),
            edges=(),
        )
        
        assert aggregate.contains_node("vendor_001") is True
        assert aggregate.contains_node("vendor_999") is False
    
    def test_aggregate_get_node_by_key(self):
        """Get node by business key."""
        case_id = uuid4()
        institution_id = uuid4()
        
        node1 = GraphNode("vendor_001", "vendor", "PT A")
        aggregate = GraphAggregate(
            case_id=case_id,
            institution_id=institution_id,
            nodes=(node1,),
            edges=(),
        )
        
        assert aggregate.get_node_by_key("vendor_001") == node1
        assert aggregate.get_node_by_key("vendor_999") is None
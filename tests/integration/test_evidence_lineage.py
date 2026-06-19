"""
Integration test: Evidence and Lineage integration
"""

import pytest


@pytest.mark.integration
def test_evidence_lineage_integration(evidence_registry, lineage_tracker):
    """Test evidence and lineage integration"""
    # Create evidence
    evidence = evidence_registry.create(
        payload={"test": "integration_data"},
        source="integration_test"
    )
    
    # Track in lineage
    evidence_node = lineage_tracker.create_node(
        node_type="evidence",
        name=evidence.id,
        metadata={"hash": evidence.hash}
    )
    
    assert evidence_node is not None
    assert evidence_node.id is not None
    assert evidence_node.type == "evidence"
    assert evidence_node.metadata.get("hash") == evidence.hash
    
    # Add processing node
    process_node = lineage_tracker.create_node(
        node_type="transform",
        name="processing"
    )
    
    # Link nodes
    lineage_tracker.add_edge(evidence_node.id, process_node.id, "consumes")
    
    # Verify path
    path = lineage_tracker.get_path(evidence_node.id, process_node.id)
    assert path is not None
    assert len(path) == 2
    assert path[0] == evidence_node.id
    assert path[1] == process_node.id


@pytest.mark.integration
def test_lineage_impact_analysis(evidence_registry, lineage_tracker):
    """Test lineage impact analysis"""
    # Create multiple evidence
    ev1 = evidence_registry.create({"data": "ev1"}, "test")
    ev2 = evidence_registry.create({"data": "ev2"}, "test")
    ev3 = evidence_registry.create({"data": "ev3"}, "test")
    
    # Create nodes
    n1 = lineage_tracker.create_node("evidence", ev1.id)
    n2 = lineage_tracker.create_node("evidence", ev2.id)
    n3 = lineage_tracker.create_node("evidence", ev3.id)
    
    # Create processing node
    processor = lineage_tracker.create_node("transform", "processor")
    
    # Connect all to processor
    lineage_tracker.add_edge(n1.id, processor.id, "consumes")
    lineage_tracker.add_edge(n2.id, processor.id, "consumes")
    lineage_tracker.add_edge(n3.id, processor.id, "consumes")
    
    # Check impact
    impact = lineage_tracker.get_impact(n1.id)
    assert processor.id in [n.id for n in impact]

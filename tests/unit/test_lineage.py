"""
Unit tests for Lineage module
"""

import pytest
from backend.lineage import LineageTracker


class TestLineageTracker:
    """Test lineage tracker"""
    
    def test_create_node(self):
        tracker = LineageTracker()
        node = tracker.create_node("test_type", "Test Node")
        
        assert node.id is not None
        assert node.type == "test_type"
        assert node.name == "Test Node"
    
    def test_add_edge(self):
        tracker = LineageTracker()
        node1 = tracker.create_node("source", "Source")
        node2 = tracker.create_node("target", "Target")
        
        edge = tracker.add_edge(node1.id, node2.id, "produces")
        
        assert edge is not None
        assert edge.source == node1.id
        assert edge.target == node2.id
    
    def test_get_path(self):
        tracker = LineageTracker()
        a = tracker.create_node("a", "A")
        b = tracker.create_node("b", "B")
        c = tracker.create_node("c", "C")
        
        tracker.add_edge(a.id, b.id, "to")
        tracker.add_edge(b.id, c.id, "to")
        
        path = tracker.get_path(a.id, c.id)
        assert path is not None
        assert len(path) == 3
    
    def test_get_metrics(self):
        tracker = LineageTracker()
        tracker.create_node("type1", "Node1")
        tracker.create_node("type1", "Node2")
        tracker.create_node("type2", "Node3")
        
        metrics = tracker.get_metrics()
        assert metrics["node_count"] == 3
        assert "node_types" in metrics
        assert metrics["node_types"]["type1"] == 2

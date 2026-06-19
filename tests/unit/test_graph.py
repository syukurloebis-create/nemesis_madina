"""
Unit tests for Graph module
"""

import pytest
from backend.graph import Graph, GraphBuilder, GraphMetrics, CollusionDetector
from backend.graph import NodeType, EdgeType


class TestGraphModels:
    """Test graph models"""
    
    def test_create_node(self):
        from backend.graph.models import GraphNode, NodeType
        node = GraphNode(
            id="node_001",
            type=NodeType.ENTITY,
            label="Test Entity",
            properties={"name": "Test"}
        )
        assert node.id == "node_001"
        assert node.type == NodeType.ENTITY
        assert node.label == "Test Entity"
    
    def test_create_edge(self):
        from backend.graph.models import GraphEdge, EdgeType
        edge = GraphEdge(
            source="node_001",
            target="node_002",
            type=EdgeType.INTERACTS,
            weight=0.8
        )
        assert edge.source == "node_001"
        assert edge.target == "node_002"
        assert edge.weight == 0.8
    
    def test_graph_add_nodes(self):
        graph = Graph()
        from backend.graph.models import GraphNode, NodeType
        node = GraphNode(id="n1", type=NodeType.ENTITY, label="Node 1")
        graph.add_node(node)
        assert "n1" in graph.nodes


class TestGraphBuilder:
    """Test graph builder"""
    
    def test_builder_creation(self):
        builder = GraphBuilder()
        assert builder is not None
    
    def test_add_node(self):
        builder = GraphBuilder()
        node = builder.add_node("test_1", NodeType.ENTITY, "Test Node")
        assert node.id == "test_1"
        assert len(builder.get_graph().nodes) == 1
    
    def test_add_edge(self):
        builder = GraphBuilder()
        builder.add_node("a", NodeType.ENTITY, "A")
        builder.add_node("b", NodeType.ENTITY, "B")
        edge = builder.add_edge("a", "b", EdgeType.INTERACTS, weight=0.9)
        
        assert edge is not None
        assert edge.source == "a"
        assert edge.target == "b"
    
    def test_get_graph(self):
        builder = GraphBuilder()
        builder.add_node("n1", NodeType.ENTITY, "Node 1")
        builder.add_node("n2", NodeType.ENTITY, "Node 2")
        
        graph = builder.get_graph()
        assert len(graph.nodes) == 2


class TestGraphMetrics:
    """Test graph metrics"""
    
    def setup_method(self):
        self.builder = GraphBuilder()
        self.builder.add_node("a", NodeType.ENTITY, "A")
        self.builder.add_node("b", NodeType.ENTITY, "B")
        self.builder.add_node("c", NodeType.ENTITY, "C")
        self.builder.add_edge("a", "b", EdgeType.INTERACTS)
        self.builder.add_edge("b", "c", EdgeType.INTERACTS)
        self.graph = self.builder.get_graph()
        self.metrics = GraphMetrics(self.graph)
    
    def test_degree_centrality(self):
        centrality = self.metrics.compute_degree_centrality()
        assert "a" in centrality
        assert "b" in centrality
        assert 0 <= centrality["a"] <= 1
    
    def test_graph_density(self):
        density = self.metrics.compute_graph_density()
        assert 0 <= density <= 1
    
    def test_clustering_coefficient(self):
        coeff = self.metrics.compute_clustering_coefficient()
        assert 0 <= coeff <= 1
    
    def test_get_summary(self):
        summary = self.metrics.get_summary()
        assert "node_count" in summary
        assert "edge_count" in summary
        assert summary["node_count"] == 3
        assert summary["edge_count"] == 2


class TestCollusionDetector:
    """Test collusion detection"""
    
    def setup_method(self):
        self.builder = GraphBuilder()
        # Create a triangle graph
        self.builder.add_node("x", NodeType.ENTITY, "X")
        self.builder.add_node("y", NodeType.ENTITY, "Y")
        self.builder.add_node("z", NodeType.ENTITY, "Z")
        self.builder.add_edge("x", "y", EdgeType.INTERACTS)
        self.builder.add_edge("y", "z", EdgeType.INTERACTS)
        self.builder.add_edge("z", "x", EdgeType.INTERACTS)
        self.graph = self.builder.get_graph()
        self.detector = CollusionDetector(self.graph)
    
    def test_detect_triangles(self):
        triangles = self.detector.detect_triangles()
        # Should find at least one triangle
        assert len(triangles) >= 1
    
    def test_compute_score(self):
        score = self.detector.compute_collusion_score()
        assert "score" in score
        assert "severity" in score
        assert 0 <= score["score"] <= 1
    
    def test_high_degree_nodes(self):
        high_degree = self.detector.detect_high_degree_nodes(threshold=1)
        assert len(high_degree) >= 1
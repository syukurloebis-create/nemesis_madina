#!/usr/bin/env python3
"""
NEMESIS - Graph Scale Test
Menguji kemampuan graph engine menangani 10k nodes dan 50k edges
"""

import sys
import time
import json
import random
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORT_DIR = PROJECT_ROOT / "reports" / "scale_tests"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class GraphScaleTester:
    """Test graph engine with large scale"""
    
    def __init__(self):
        self.memory_samples = []
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def record_memory(self):
        """Record current memory usage"""
        self.memory_samples.append({
            "timestamp": time.time(),
            "memory_mb": self.get_memory_usage()
        })
    
    def create_test_data(self, node_count: int = 10000, edge_count: int = 50000) -> Tuple[List, List]:
        """Create test nodes and edges"""
        print(f"  Creating {node_count} nodes...")
        nodes = []
        for i in range(node_count):
            nodes.append({
                "id": f"node_{i}",
                "label": f"Node {i}",
                "type": "entity"
            })
        
        print(f"  Creating {edge_count} edges...")
        edges = []
        for i in range(edge_count):
            src = random.randint(0, node_count - 1)
            dst = random.randint(0, node_count - 1)
            edges.append({
                "source": f"node_{src}",
                "target": f"node_{dst}",
                "type": "interacts",
                "weight": random.uniform(0.1, 1.0)
            })
        
        return nodes, edges
    
    def test_graph_builder(self, node_count: int = 10000, edge_count: int = 50000) -> Dict[str, Any]:
        """Test graph builder performance"""
        from backend.graph import GraphBuilder, NodeType, EdgeType
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}GRAPH SCALE TEST - {node_count} nodes, {edge_count} edges{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        # Record baseline
        self.record_memory()
        baseline_memory = self.memory_samples[-1]["memory_mb"]
        print(f"📊 Baseline memory: {baseline_memory:.2f} MB")
        
        builder = GraphBuilder()
        
        # Create nodes
        print(f"\n📝 Building {node_count} nodes...")
        start_time = time.time()
        
        for i in range(node_count):
            builder.add_node(f"node_{i}", NodeType.ENTITY, f"Node {i}")
            if (i + 1) % 2000 == 0:
                print(f"  Created {i+1}/{node_count} nodes")
        
        node_time = time.time() - start_time
        self.record_memory()
        print(f"  ✅ Nodes created in {node_time:.2f}s")
        
        # Create edges
        print(f"\n🔗 Building {edge_count} edges...")
        start_time = time.time()
        
        # Pre-create list of node IDs for faster random access
        node_ids = [f"node_{i}" for i in range(node_count)]
        
        for i in range(edge_count):
            src = random.choice(node_ids)
            dst = random.choice(node_ids)
            builder.add_edge(src, dst, EdgeType.INTERACTS, weight=random.uniform(0.1, 1.0))
            if (i + 1) % 10000 == 0:
                print(f"  Created {i+1}/{edge_count} edges")
        
        edge_time = time.time() - start_time
        self.record_memory()
        print(f"  ✅ Edges created in {edge_time:.2f}s")
        
        # Get final graph
        graph = builder.get_graph()
        final_memory = self.memory_samples[-1]["memory_mb"]
        memory_increase = final_memory - baseline_memory
        
        # Calculate metrics
        total_time = node_time + edge_time
        
        # Test graph metrics
        print(f"\n📊 Computing graph metrics...")
        from backend.graph import GraphMetrics
        metrics = GraphMetrics(graph)
        
        start_time = time.time()
        summary = metrics.get_summary()
        metrics_time = time.time() - start_time
        
        print(f"  ✅ Metrics computed in {metrics_time:.2f}s")
        print(f"     - Density: {summary['density']:.6f}")
        print(f"     - Clustering coefficient: {summary['clustering_coefficient']:.4f}")
        print(f"     - Diameter: {summary['diameter']}")
        
        # Results
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}RESULTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"  Nodes created:     {len(graph.nodes)}")
        print(f"  Edges created:     {len(graph.edges)}")
        print(f"  Build time:        {total_time:.2f}s")
        print(f"  Memory increase:   {memory_increase:.1f} MB")
        print(f"  Final memory:      {final_memory:.1f} MB")
        print(f"  Metrics time:      {metrics_time:.2f}s")
        
        # Determine status
        status = "PASSED" if total_time < 5 else "WARNING" if total_time < 10 else "FAILED"
        status_color = GREEN if status == "PASSED" else YELLOW if status == "WARNING" else RED
        
        print(f"\n  Status: {status_color}{status}{RESET}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "build_time_seconds": round(total_time, 2),
            "node_time_seconds": round(node_time, 2),
            "edge_time_seconds": round(edge_time, 2),
            "metrics_time_seconds": round(metrics_time, 2),
            "baseline_memory_mb": round(baseline_memory, 1),
            "final_memory_mb": round(final_memory, 1),
            "memory_increase_mb": round(memory_increase, 1),
            "graph_density": summary['density'],
            "clustering_coefficient": summary['clustering_coefficient'],
            "diameter": summary['diameter'],
            "status": status
        }
    
    def test_collusion_detection(self, node_count: int = 5000, edge_count: int = 20000) -> Dict[str, Any]:
        """Test collusion detection on large graph"""
        from backend.graph import GraphBuilder, NodeType, EdgeType, CollusionDetector
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}COLLUSION DETECTION SCALE TEST{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        builder = GraphBuilder()
        
        # Create triangle-heavy graph for collusion detection
        print(f"  Creating triangle-heavy graph...")
        
        # Create clusters of 10 nodes each with high internal connectivity
        cluster_size = 10
        num_clusters = node_count // cluster_size
        
        for cluster in range(num_clusters):
            base = cluster * cluster_size
            # Create nodes in cluster
            for i in range(cluster_size):
                node_id = f"c{cluster}_n{i}"
                builder.add_node(node_id, NodeType.ENTITY, f"Node {node_id}")
            
            # Create internal edges (high density)
            for i in range(cluster_size):
                for j in range(i + 1, cluster_size):
                    builder.add_edge(f"c{cluster}_n{i}", f"c{cluster}_n{j}", EdgeType.INTERACTS)
        
        graph = builder.get_graph()
        
        print(f"  Graph created: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
        # Run collusion detection
        print(f"\n🔍 Running collusion detection...")
        start_time = time.time()
        detector = CollusionDetector(graph)
        score = detector.compute_collusion_score()
        detection_time = time.time() - start_time
        
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}COLLUSION RESULTS{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"  Detection time:    {detection_time:.2f}s")
        print(f"  Collusion score:   {score['score']}")
        print(f"  Severity:          {score['severity']}")
        print(f"  Triangles found:   {score['triangle_count']}")
        print(f"  Hubs detected:     {score['hub_count']}")
        
        status = "PASSED" if detection_time < 2 else "WARNING"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "detection_time_seconds": round(detection_time, 2),
            "collusion_score": score['score'],
            "severity": score['severity'],
            "triangle_count": score['triangle_count'],
            "hub_count": score['hub_count'],
            "status": status
        }


def main():
    tester = GraphScaleTester()
    
    # Test 1: Graph builder scale
    result1 = tester.test_graph_builder(10000, 50000)
    
    # Save results
    report_path = REPORT_DIR / f"graph_scale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump(result1, f, indent=2, default=str)
    
    print(f"\n📄 Report saved: {report_path}")
    
    # Test 2: Collusion detection (optional, can be heavy)
    # result2 = tester.test_collusion_detection(5000, 20000)
    
    return 0 if result1["status"] != "FAILED" else 1


if __name__ == "__main__":
    sys.exit(main())
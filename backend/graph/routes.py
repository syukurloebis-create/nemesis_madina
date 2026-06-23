"""Graph API Routes"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

from graph.builder import GraphBuilder
from graph.models import NodeType, EdgeType
from graph.metrics import GraphMetrics


router = APIRouter(
    prefix="/graph",
    tags=["graph"]
)


@router.get("/")
async def get_graph():
    """Get current graph"""
    builder = GraphBuilder()
    graph = builder.get_graph()
    return {
        "nodes": list(graph.nodes.keys()),
        "edges": len(graph.edges),
        "metrics": GraphMetrics(graph).get_summary()
    }


@router.post("/nodes")
async def add_node(node_id: str, label: str, node_type: str = "entity"):
    """Add node to graph"""
    builder = GraphBuilder()
    try:
        node_type_enum = NodeType(node_type)
    except ValueError:
        node_type_enum = NodeType.ENTITY

    node = builder.add_node(node_id, node_type_enum, label)
    return {"id": node.id, "label": node.label, "type": node.type.value}


@router.post("/edges")
async def add_edge(source: str, target: str, edge_type: str = "interacts", weight: float = 1.0):
    """Add edge to graph"""
    builder = GraphBuilder()
    try:
        edge_type_enum = EdgeType(edge_type)
    except ValueError:
        edge_type_enum = EdgeType.INTERACTS

    edge = builder.add_edge(source, target, edge_type_enum, weight)
    if not edge:
        raise HTTPException(status_code=400, detail="Nodes not found")
    return {"source": source, "target": target, "type": edge_type, "weight": weight}


@router.get("/metrics")
async def get_graph_metrics():
    """Get graph metrics"""
    builder = GraphBuilder()
    metrics = GraphMetrics(builder.get_graph())
    return metrics.get_summary()


@router.get("/nodes/{node_id}/neighbors")
async def get_neighbors(node_id: str):
    """Get neighbors of a node"""
    builder = GraphBuilder()
    graph = builder.get_graph()
    neighbors = graph.get_neighbors(node_id)
    return {"node_id": node_id, "neighbors": neighbors}

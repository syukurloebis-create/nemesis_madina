from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/")
async def get_graph():
    return {"nodes": [], "edges": [], "metrics": {"node_count": 0, "edge_count": 0}}


@router.post("/nodes")
async def add_node(node_id: str, label: str, properties: Dict[str, Any] = None):
    return {"node_id": node_id, "label": label, "message": "Node added"}


@router.post("/edges")
async def add_edge(source: str, target: str, label: str, weight: float = 1.0):
    return {"source": source, "target": target, "label": label, "message": "Edge added"}


@router.get("/nodes/{node_id}/neighbors")
async def get_neighbors(node_id: str, direction: str = "both"):
    return {"node_id": node_id, "neighbors": []}


@router.get("/metrics")
async def get_graph_metrics():
    return {"node_count": 0, "edge_count": 0, "density": 0.0}

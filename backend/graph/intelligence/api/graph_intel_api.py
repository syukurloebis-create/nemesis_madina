"""Graph Intelligence API Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from uuid import UUID

from backend.graph.intelligence.repositories.entity_edge_repo import EntityEdgeRepository
from backend.graph.intelligence.models import (
    EntityNode, EntityEdge, CollusionDetectionResult,
    EntityType, RelationshipType
)

router = APIRouter(prefix="/graph-intel", tags=["graph-intelligence"])


async def get_edge_repo():
    from backend.infrastructure.database import get_pool
    pool = await get_pool()
    return EntityEdgeRepository(pool)


@router.post("/nodes", response_model=EntityNode)
async def add_node(
    node: EntityNode,
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Add entity node to graph"""
    return await repo.add_node(node)


@router.post("/edges", response_model=EntityEdge)
async def add_edge(
    edge: EntityEdge,
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Add relationship edge to graph"""
    return await repo.add_edge(edge)


@router.get("/nodes/{node_id}/neighbors")
async def get_neighbors(
    node_id: str,
    depth: int = Query(2, ge=1, le=5),
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Get neighbors of a node"""
    neighbors = await repo.get_neighbors(node_id, depth)
    return {"node_id": node_id, "neighbors": neighbors, "depth": depth}


@router.get("/relationships")
async def get_relationships(
    source_id: str,
    target_id: str,
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Get relationships between two entities"""
    relationships = await repo.get_relationships(source_id, target_id)
    return {
        "source": source_id,
        "target": target_id,
        "relationships": [rel.dict() for rel in relationships]
    }


@router.get("/network/metrics")
async def get_network_metrics(
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Get network metrics for entity graph"""
    return await repo.get_network_metrics()


@router.get("/connected/{entity_id}")
async def get_connected_entities(
    entity_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Find all entities connected to given entity"""
    connected = await repo.find_connected_entities(entity_id, max_depth)
    return {
        "entity_id": entity_id,
        "connected_entities": connected,
        "count": len(connected)
    }


@router.get("/entities/by-type/{entity_type}")
async def get_entities_by_type(
    entity_type: EntityType,
    repo: EntityEdgeRepository = Depends(get_edge_repo)
):
    """Get all entities of a specific type"""
    return {"entity_type": entity_type.value, "entities": []}

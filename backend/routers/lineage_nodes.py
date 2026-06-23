from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from security.dependencies import get_current_active_user
from security.models import User

router = APIRouter(prefix="/lineage", tags=["lineage"])

# Mock data untuk nodes
MOCK_NODES = [
    {"id": "node-1", "label": "PT. Maju Jaya", "type": "vendor", "risk_score": 92},
    {"id": "node-2", "label": "CV. Karya Mandiri", "type": "vendor", "risk_score": 88},
    {"id": "node-3", "label": "Kementerian PUPR", "type": "institution", "risk_score": 65},
    {"id": "node-4", "label": "PT. Bangun Nusantara", "type": "vendor", "risk_score": 78},
    {"id": "node-5", "label": "Dr. Ahmad Fauzi", "type": "individual", "risk_score": 58},
]

MOCK_EDGES = [
    {"from": "node-1", "to": "node-3", "type": "contract", "confidence": 88},
    {"from": "node-2", "to": "node-3", "type": "contract", "confidence": 92},
    {"from": "node-1", "to": "node-2", "type": "collusion", "confidence": 75},
    {"from": "node-4", "to": "node-3", "type": "contract", "confidence": 85},
    {"from": "node-5", "to": "node-3", "type": "oversight", "confidence": 90},
]


@router.get("/nodes")
async def get_lineage_nodes(
    current_user: User = Depends(get_current_active_user)
):
    """Get all lineage nodes"""
    return {"data": MOCK_NODES, "total": len(MOCK_NODES)}


@router.get("/relationships")
async def get_lineage_relationships(
    current_user: User = Depends(get_current_active_user)
):
    """Get all lineage relationships/edges"""
    return {"data": MOCK_EDGES, "total": len(MOCK_EDGES)}


@router.get("/node/{node_id}/lineage")
async def get_node_lineage(
    node_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get lineage for a specific node"""
    node = next((n for n in MOCK_NODES if n["id"] == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Get related edges
    edges = [e for e in MOCK_EDGES if e["from"] == node_id or e["to"] == node_id]
    
    return {
        "node": node,
        "relationships": edges,
        "degree": len(edges)
    }


@router.get("/node/{node_id}/verify")
async def verify_node_lineage(
    node_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Verify lineage integrity for a node"""
    return {
        "node_id": node_id,
        "verified": True,
        "chain_length": 3,
        "integrity_score": 100,
        "verified_at": datetime.now().isoformat()
    }

from fastapi import APIRouter

# Router TANPA prefix (main.py yang akan handle)
router = APIRouter(tags=["Graph"])

async def graph_summary():
    return {
        "total_relationships":7442,
        "total_entities":549
    }

@router.get("/metrics")
async def get_graph_metrics():
    return {
        "total_entities": 549,
        "total_relationships": 7442,
        "collusion_edges": 0
    }

@router.get("/entities")
async def get_graph_entities():
    return {
        "entities": [
            {"id": "ent-1", "name": "Entity 1", "type": "VENDOR"},
            {"id": "ent-2", "name": "Entity 2", "type": "PERSON"}
        ]
    }

@router.get("/key-actors")
async def get_key_actors():
    return [
        {"id": "actor-1", "name": "Vendor X", "influence": 85},
        {"id": "actor-2", "name": "Employee Y", "influence": 72}
    ]

@router.get("/collusion/{case_id}")
async def get_collusion(case_id: str):
    return {
        "case_id": case_id,
        "collusion_detected": True,
        "confidence": 0.85,
        "entities": ["Vendor X", "Employee Y"]
    }

@router.get("/stats")
async def get_graph_stats():
    return {
        "total_entities": 549,
        "total_relationships": 7442,
        "communities": 12
    }

@router.get("")
async def graph():

    return await graph_summary()

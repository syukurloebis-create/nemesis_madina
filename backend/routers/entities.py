from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from backend.infrastructure.database import get_db
from backend.security.dependencies import get_current_active_user
from backend.security.models import User

router = APIRouter(prefix="/entities", tags=["entities"])


# Entity Models
class EntityResponse:
    def __init__(self, id: str, name: str, entity_type: str, risk_score: int, 
                 risk_level: str, metadata: Dict, created_at: str, updated_at: str):
        self.id = id
        self.name = name
        self.type = entity_type
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at


# Mock data untuk development
MOCK_ENTITIES = [
    {
        "id": "1",
        "name": "PT. Maju Jaya",
        "type": "vendor",
        "risk_score": 92,
        "risk_level": "critical",
        "related_cases": 5,
        "metadata": {"registration": "1234567890", "established": "2010"},
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-06-01T00:00:00"
    },
    {
        "id": "2",
        "name": "CV. Karya Mandiri",
        "type": "vendor",
        "risk_score": 88,
        "risk_level": "high",
        "related_cases": 3,
        "metadata": {"registration": "9876543210", "established": "2015"},
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-06-01T00:00:00"
    },
    {
        "id": "3",
        "name": "Kementerian PUPR",
        "type": "institution",
        "risk_score": 65,
        "risk_level": "medium",
        "related_cases": 2,
        "metadata": {"institution_type": "government"},
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-06-01T00:00:00"
    },
    {
        "id": "4",
        "name": "PT. Bangun Nusantara",
        "type": "vendor",
        "risk_score": 78,
        "risk_level": "high",
        "related_cases": 4,
        "metadata": {"registration": "5555555555", "established": "2008"},
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-06-01T00:00:00"
    },
    {
        "id": "5",
        "name": "Dr. Ahmad Fauzi",
        "type": "individual",
        "risk_score": 58,
        "risk_level": "medium",
        "related_cases": 1,
        "metadata": {"position": "Pejabat"},
        "created_at": "2026-01-01T00:00:00",
        "updated_at": "2026-06-01T00:00:00"
    }
]


@router.get("/")
async def get_entities(
    search: Optional[str] = None,
    entity_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all entities with pagination and filters"""
    try:
        # Try to get from database, fallback to mock
        entities = MOCK_ENTITIES.copy()
        
        # Apply filters
        if search:
            entities = [e for e in entities if search.lower() in e["name"].lower()]
        if entity_type:
            entities = [e for e in entities if e["type"] == entity_type]
        if risk_level:
            entities = [e for e in entities if e["risk_level"] == risk_level]
        
        # Pagination
        total = len(entities)
        entities = entities[offset:offset + limit]
        
        return {
            "data": entities,
            "total": total,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entity_id}")
async def get_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get entity by ID"""
    entity = next((e for e in MOCK_ENTITIES if e["id"] == entity_id), None)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/{entity_id}/cases")
async def get_entity_cases(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get cases related to entity"""
    # Mock cases for entity
    mock_cases = [
        {"id": "case-001", "title": "Fraud Investigation", "status": "investigating", "created_at": "2026-06-01"},
        {"id": "case-002", "title": "Collusion Detection", "status": "open", "created_at": "2026-05-28"}
    ]
    return {"data": mock_cases, "total": len(mock_cases)}


@router.post("/")
async def create_entity(
    entity_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new entity"""
    new_entity = {
        "id": str(uuid.uuid4()),
        "name": entity_data.get("name"),
        "type": entity_data.get("type", "unknown"),
        "risk_score": entity_data.get("risk_score", 50),
        "risk_level": "medium",
        "related_cases": 0,
        "metadata": entity_data.get("metadata", {}),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    MOCK_ENTITIES.append(new_entity)
    return {"data": new_entity, "message": "Entity created successfully"}


@router.put("/{entity_id}")
async def update_entity(
    entity_id: str,
    entity_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update entity"""
    entity = next((e for e in MOCK_ENTITIES if e["id"] == entity_id), None)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    entity.update(entity_data)
    entity["updated_at"] = datetime.now().isoformat()
    return {"data": entity, "message": "Entity updated successfully"}


@router.delete("/{entity_id}")
async def delete_entity(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete entity"""
    global MOCK_ENTITIES
    entity = next((e for e in MOCK_ENTITIES if e["id"] == entity_id), None)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    MOCK_ENTITIES = [e for e in MOCK_ENTITIES if e["id"] != entity_id]
    return {"message": "Entity deleted successfully"}

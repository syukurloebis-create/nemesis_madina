# backend/services/case_service.py
from typing import Optional, Dict, Any, List  # ← TAMBAHKAN IMPORT INI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import uuid
import logging

from domain.case_aggregate import CaseAggregate
from domain.event_sourcing_repository import EventSourcingRepository
from backend.models.existing import Case as CaseModel

logger = logging.getLogger(__name__)


class CaseService:
    """Service for case management using event sourcing"""
    
    def __init__(self, session: AsyncSession, tenant_id: str = None):
        self.session = session
        self.tenant_id = tenant_id
        self.event_repo = EventSourcingRepository(session, tenant_id)
    
    async def create_case(self, title: str, description: str, created_by: str) -> Dict[str, Any]:
        """Create new case"""
        case_id = uuid.uuid4()
        case = CaseAggregate(case_id)
        case.create(title, description, created_by)
        
        await self.event_repo.save(case)
        
        # Update read model
        await self._update_read_model(case)
        
        return case.to_dict()
    
    async def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case by ID (from read model for performance)"""
        query = text("""
            SELECT id, title, description, status, priority, 
                   assigned_to, tags, created_at, updated_at
            FROM cases
            WHERE id = :case_id
        """)
        
        result = await self.session.execute(query, {"case_id": case_id})
        row = result.fetchone()
        
        if row:
            return {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "assigned_to": row[5],
                "tags": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None
            }
        return None
    
    async def update_case(self, case_id: str, title: str = None, 
                          description: str = None, actor_id: str = None) -> Dict[str, Any]:
        """Update case using event sourcing"""
        case = await self.event_repo.load(CaseAggregate, case_id)
        
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        case.update(title=title, description=description, actor_id=actor_id)
        await self.event_repo.save(case)
        
        await self._update_read_model(case)
        
        return case.to_dict()
    
    async def change_status(self, case_id: str, new_status: str, reason: str, actor_id: str):
        """Change case status"""
        case = await self.event_repo.load(CaseAggregate, case_id)
        
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        case.change_status(new_status, reason, actor_id)
        await self.event_repo.save(case)
        await self._update_read_model(case)
        
        return case.to_dict()
    
    async def assign_case(self, case_id: str, assignee_id: str, assigned_by: str):
        """Assign case to investigator"""
        case = await self.event_repo.load(CaseAggregate, case_id)
        
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        case.assign(assignee_id, assigned_by)
        await self.event_repo.save(case)
        await self._update_read_model(case)
        
        return case.to_dict()
    
    async def close_case(self, case_id: str, reason: str, closed_by: str):
        """Close case"""
        case = await self.event_repo.load(CaseAggregate, case_id)
        
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        case.close(reason, closed_by)
        await self.event_repo.save(case)
        await self._update_read_model(case)
        
        return case.to_dict()
    
    async def _update_read_model(self, case: CaseAggregate):
        """Update read model with aggregate state"""
        query = text("""
            INSERT INTO cases (id, title, description, status, priority, 
                              assigned_to, tags, updated_at, tenant_id)
            VALUES (:id, :title, :description, :status, :priority,
                    :assigned_to, :tags, :updated_at, :tenant_id)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                status = EXCLUDED.status,
                priority = EXCLUDED.priority,
                assigned_to = EXCLUDED.assigned_to,
                tags = EXCLUDED.tags,
                updated_at = EXCLUDED.updated_at
        """)
        
        await self.session.execute(query, {
            "id": str(case.id),
            "title": case.title,
            "description": case.description,
            "status": case.status,
            "priority": case.priority,
            "assigned_to": case.assigned_to,
            "tags": case.tags,
            "updated_at": datetime.utcnow(),
            "tenant_id": self.tenant_id
        })
        await self.session.commit()
    
    async def list_cases(self, status: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List cases from read model"""
        query = "SELECT id, title, description, status, priority, assigned_to, created_at, updated_at FROM cases"
        params = {}
        
        if status:
            query += " WHERE status = :status"
            params["status"] = status
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = await self.session.execute(text(query), params)
        rows = result.fetchall()
        
        return [
            {
                "id": str(r[0]),
                "title": r[1],
                "description": r[2],
                "status": r[3],
                "priority": r[4],
                "assigned_to": r[5],
                "created_at": r[6].isoformat() if r[6] else None,
                "updated_at": r[7].isoformat() if r[7] else None
            }
            for r in rows
        ]
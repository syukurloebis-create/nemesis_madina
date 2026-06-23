from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from models.event import Event
from cases.models import Case, CaseStatus, CasePriority
from cases.event_store import (
    append_event, 
    get_case_events, 
    get_last_event,
    validate_chain,
    compute_event_hash
)


class CaseService:
    """Service layer for case management with immutable event sourcing"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_case(
        self,
        title: str,
        description: Optional[str] = None,
        priority: CasePriority = CasePriority.MEDIUM,
        case_metadata: Dict[str, Any] = None,
        assigned_to: Optional[str] = None,
        created_by: Optional[str] = None,
        institution_id: Optional[str] = None,
    ) -> Case:
        """Create a new case with initial event"""
        # Handle created_by - default to system UUID if not provided
        if not created_by or created_by == "system":
            created_by = "00000000-0000-0000-0000-000000000000"
        
        case_id = str(uuid.uuid4())
        
        case = Case(
            id=case_id,
            title=title,
            description=description,
            status="OPEN",
            priority=priority.value if hasattr(priority, "value") else str(priority),
            assigned_to=assigned_to,
            metadata=case_metadata or {},
            institution_id=institution_id,
            created_by=created_by,
        )
        
        self.session.add(case)

        # Create event using modern event store
        # Compute event_hash
        import hashlib
        import json
        payload_str = json.dumps({
            "title": title,
            "description": description,
            "priority": priority.value if hasattr(priority, 'value') else str(priority),
            "status": "OPEN",
            "metadata": case_metadata or {},
            "assigned_to": assigned_to,
            "created_by": created_by,
        }, sort_keys=True)
        event_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        event = Event(
            id=uuid.uuid4(),
            aggregate_id=uuid.UUID(case_id),
            aggregate_type="CASE",
            event_type="CASE_CREATED",
            event_version=1,
            payload={
                "title": title,
                "description": description,
                "priority": priority.value if hasattr(priority, 'value') else str(priority),
                "status": "OPEN",
                "metadata": case_metadata or {},
                "assigned_to": assigned_to,
                "created_by": created_by,
            },
            event_hash=event_hash,
            tenant_id=uuid.UUID('11111111-1111-1111-1111-111111111111'),
            created_by=uuid.UUID(created_by) if created_by and created_by != "system" and len(created_by) == 36 else None
        )
        self.session.add(event)
        
        
        await self.session.commit()
        await self.session.refresh(case)
        
        return case
    
    async def get_case(self, case_id: UUID) -> Optional[Case]:
        """Get case by ID"""
        result = await self.session.execute(
            select(Case).where(Case.id == case_id, Case.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_all_cases(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CaseStatus] = None,
        priority: Optional[CasePriority] = None,
        institution_id: Optional[str] = None,
    ) -> List[Case]:
        """Get all cases with filters"""
        query = select(Case).where(Case.is_deleted == False)
        
        if status:
            query = query.where(Case.status == status)
        if priority:
            query = query.where(Case.priority == priority)
        if institution_id:
            query = query.where(Case.institution_id == institution_id)
        
        query = query.offset(skip).limit(limit).order_by(Case.created_at.desc())
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def update_case(
        self,
        case_id: UUID,
        updated_by: str = "system",
        **kwargs
    ) -> Optional[Case]:
        """Update case with event logging"""
        
        case = await self.get_case(case_id)
        if not case:
            return None
        
        # Track what changed for event
        changes = {}
        for key, value in kwargs.items():
            if hasattr(case, key) and value is not None:
                old_value = getattr(case, key)
                if old_value != value:
                    changes[key] = {"old": old_value, "new": value}
                    setattr(case, key, value)
        
        case.updated_at = datetime.utcnow()
        
        # Get last event for hash chain
        last_event = await get_last_event(self.session, case_id)
        previous_hash = last_event.event_hash if last_event else None
        
        # Create update event
        await append_event(
            session=self.session,
            case_id=case_id,
            event_type="case_updated",
            data={
                "changes": changes,
                "updated_by": updated_by,
                "timestamp": datetime.utcnow().isoformat(),
            },
            previous_hash=previous_hash
        )
        
        await self.session.commit()
        await self.session.refresh(case)
        
        return case
    
    async def get_case_events(self, case_id: UUID) -> List:
        """Get all events for a case"""
        return await get_case_events(self.session, case_id)
    
    async def verify_lineage(self, case_id: UUID) -> Dict[str, Any]:
        """Verify hash chain integrity"""
        events = await get_case_events(self.session, case_id)
        is_valid, broken_at = validate_chain(events)
        
        return {
            "chain_valid": is_valid,
            "broken_at_sequence": broken_at,
            "total_events": len(events),
        }
    
    async def soft_delete_case(self, case_id: UUID, deleted_by: str = "system") -> bool:
        """Soft delete a case"""
        case = await self.get_case(case_id)
        if not case:
            return False
        
        case.is_deleted = True
        case.deleted_at = datetime.utcnow()
        case.deleted_by = deleted_by
        
        # Get last event for hash chain
        last_event = await get_last_event(self.session, case_id)
        previous_hash = last_event.event_hash if last_event else None
        
        await append_event(
            session=self.session,
            case_id=case_id,
            event_type="case_deleted",
            data={
                "deleted_by": deleted_by,
                "deleted_at": datetime.utcnow().isoformat(),
            },
            previous_hash=previous_hash
        )
        
        await self.session.commit()
        return True
    
    async def get_cases_count_by_status(self) -> Dict[str, int]:
        """Get count of cases grouped by status"""
        result = await self.session.execute(
            select(Case.status, func.count(Case.id))
            .where(Case.is_deleted == False)
            .group_by(Case.status)
        )
        return {status.value: count for status, count in result.all()}
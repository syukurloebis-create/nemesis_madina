from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
import uuid

from backend.cases.models import Case, CasePriority


class CaseRepository:
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        title: str,
        description: Optional[str] = None,
        priority: CasePriority = CasePriority.MEDIUM,
        case_metadata: Optional[Dict] = None,
        assigned_to: Optional[str] = None,
        institution_id: Optional[str] = None,
    ) -> Case:
        case = Case(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            case_metadata=case_metadata or {},
            assigned_to=assigned_to,
            institution_id=institution_id,
        )
        self.session.add(case)
        await self.session.flush()
        return case
    
    async def get_all(self) -> List[Case]:
        result = await self.session.execute(select(Case))
        return list(result.scalars().all())

    async def get(self, case_id: str) -> Optional[Case]:
        """Get a case by ID"""
        from sqlalchemy import select
        result = await self.session.execute(select(Case).where(Case.id == case_id))
        return result.scalar_one_or_none()

    async def update(self, case_id: str, **kwargs) -> Optional[Case]:
        """Update a case by ID"""
        from sqlalchemy import select
        
        result = await self.session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            return None
        
        allowed_fields = {"title", "description", "status", "priority", "assigned_to", "case_metadata"}
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(case, key, value)
        
        await self.session.flush()
        await self.session.refresh(case)
        
        return case

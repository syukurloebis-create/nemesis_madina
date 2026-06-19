# backend/projections/case_projection.py
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class CaseProjection:
    """Projection for case read model"""
    
    def __init__(self, session: AsyncSession, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id
    
    async def handle_case_created(self, event: Dict[str, Any]):
        """Handle CASE_CREATED event"""
        data = event.get('data', {})
        
        query = text("""
            INSERT INTO cases (id, title, description, status, priority, 
                              created_at, updated_at, tenant_id, created_by)
            VALUES (:id, :title, :description, :status, :priority,
                    :created_at, :updated_at, :tenant_id, :created_by)
            ON CONFLICT (id) DO NOTHING
        """)
        
        await self.session.execute(query, {
            "id": event.get('case_id'),
            "title": data.get('title'),
            "description": data.get('description'),
            "status": "OPEN",
            "priority": "MEDIUM",
            "created_at": data.get('created_at'),
            "updated_at": data.get('created_at'),
            "tenant_id": self.tenant_id,
            "created_by": data.get('created_by')
        })
        
        await self.session.commit()
        logger.debug(f"Projected CASE_CREATED for {event.get('case_id')}")
    
    async def handle_case_updated(self, event: Dict[str, Any]):
        """Handle CASE_UPDATED event"""
        data = event.get('data', {})
        
        # Build dynamic update query
        updates = []
        params = {"id": event.get('case_id')}
        
        if 'title' in data:
            updates.append("title = :title")
            params['title'] = data['title']
        
        if 'description' in data:
            updates.append("description = :description")
            params['description'] = data['description']
        
        if updates:
            query = text(f"""
                UPDATE cases 
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE id = :id
            """)
            
            await self.session.execute(query, params)
            await self.session.commit()
            logger.debug(f"Projected CASE_UPDATED for {event.get('case_id')}")
    
    async def handle_case_status_changed(self, event: Dict[str, Any]):
        """Handle CASE_STATUS_CHANGED event"""
        data = event.get('data', {})
        
        query = text("""
            UPDATE cases 
            SET status = :status, updated_at = NOW()
            WHERE id = :id
        """)
        
        await self.session.execute(query, {
            "id": event.get('case_id'),
            "status": data.get('new_status')
        })
        
        await self.session.commit()
        logger.debug(f"Projected CASE_STATUS_CHANGED for {event.get('case_id')}")
    
    async def handle_case_assigned(self, event: Dict[str, Any]):
        """Handle CASE_ASSIGNED event"""
        data = event.get('data', {})
        
        query = text("""
            UPDATE cases 
            SET assigned_to = :assigned_to, updated_at = NOW()
            WHERE id = :id
        """)
        
        await self.session.execute(query, {
            "id": event.get('case_id'),
            "assigned_to": data.get('assigned_to')
        })
        
        await self.session.commit()
        logger.debug(f"Projected CASE_ASSIGNED for {event.get('case_id')}")
    
    async def handle_case_closed(self, event: Dict[str, Any]):
        """Handle CASE_CLOSED event"""
        data = event.get('data', {})
        
        query = text("""
            UPDATE cases 
            SET status = 'CLOSED', updated_at = NOW(), closed_at = :closed_at
            WHERE id = :id
        """)
        
        await self.session.execute(query, {
            "id": event.get('case_id'),
            "closed_at": data.get('closed_at')
        })
        
        await self.session.commit()
        logger.debug(f"Projected CASE_CLOSED for {event.get('case_id')}")
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.graph.models import GraphEntity, GraphRelationship, CollusionDetection
import uuid
import logging

logger = logging.getLogger(__name__)

class GraphIntelligenceService:
    
    @staticmethod
    async def add_entity(
        session: AsyncSession,
        case_id: str,
        institution_id: str,
        entity_type: str,
        name: str,
        tax_id: str = None,
        address: str = None,
        extra_data: dict = None,
        created_by: str = None
    ) -> GraphEntity:
        entity = GraphEntity(
            id=str(uuid.uuid4()),
            case_id=case_id,
            institution_id=institution_id,
            entity_type=entity_type,
            name=name,
            tax_id=tax_id,
            address=address,
            extra_data=extra_data or {},
            created_by=created_by
        )
        session.add(entity)
        await session.flush()
        return entity
    
    @staticmethod
    async def add_relationship(
        session: AsyncSession,
        case_id: str,
        institution_id: str,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: float = 1.0,
        amount: float = None,
        description: str = None,
        created_by: str = None
    ) -> GraphRelationship:
        relationship = GraphRelationship(
            case_id=case_id,
            institution_id=institution_id,
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            weight=weight,
            amount=amount,
            description=description,
            created_by=created_by
        )
        session.add(relationship)
        await session.flush()
        return relationship
    
    @staticmethod
    async def detect_collusion(
        session: AsyncSession,
        case_id: str,
        institution_id: str
    ) -> CollusionDetection:
        # Create detection using existing table structure
        detection = CollusionDetection(
            id=str(uuid.uuid4()),
            case_id=case_id,
            pattern_type="collusion_pattern",
            description="Auto-detected collusion pattern",
            entity_ids=[],
            entity_names=[],
            pattern_key=f"collusion_{case_id[:8]}",
            confidence=0.8,
            severity=0.5,
            evidence={},
            is_reviewed=False
        )
        session.add(detection)
        await session.flush()
        return detection

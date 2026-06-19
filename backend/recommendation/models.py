from enum import Enum
from typing import Optional
from datetime import datetime
from dataclasses import dataclass
import uuid


class RecommendationType(str, Enum):
    REVIEW = "REVIEW"
    AUDIT = "AUDIT"
    ESCALATE = "ESCALATE"
    RECOVER = "RECOVER"
    POLICY_CHANGE = "POLICY_CHANGE"
    OTHER = "OTHER"


class RecommendationStatus(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    ISSUED = "ISSUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


@dataclass
class Recommendation:
    recommendation_id: uuid.UUID
    finding_id: uuid.UUID
    recommendation_type: RecommendationType
    target_entity: str
    description: str
    due_date: Optional[datetime]
    status: RecommendationStatus
    created_by: uuid.UUID
    created_at: datetime
    issued_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "recommendation_id": str(self.recommendation_id),
            "finding_id": str(self.finding_id),
            "recommendation_type": self.recommendation_type.value,
            "target_entity": self.target_entity,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status.value,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat(),
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class RecommendationService:
    def __init__(self, db_session):
        self.session = db_session
        self._recommendations = {}
    
    async def create_recommendation(
        self,
        finding_id: uuid.UUID,
        recommendation_type: RecommendationType,
        target_entity: str,
        description: str,
        created_by: uuid.UUID,
        due_date: Optional[datetime] = None
    ) -> Recommendation:
        rec = Recommendation(
            recommendation_id=uuid.uuid4(),
            finding_id=finding_id,
            recommendation_type=recommendation_type,
            target_entity=target_entity,
            description=description,
            due_date=due_date,
            status=RecommendationStatus.DRAFT,
            created_by=created_by,
            created_at=datetime.utcnow()
        )
        self._recommendations[rec.recommendation_id] = rec
        return rec
    
    async def issue_recommendation(self, recommendation_id: uuid.UUID) -> Optional[Recommendation]:
        rec = self._recommendations.get(recommendation_id)
        if rec and rec.status == RecommendationStatus.APPROVED:
            rec.status = RecommendationStatus.ISSUED
            rec.issued_at = datetime.utcnow()
        return rec
    
    async def update_status(
        self,
        recommendation_id: uuid.UUID,
        status: RecommendationStatus
    ) -> Optional[Recommendation]:
        rec = self._recommendations.get(recommendation_id)
        if rec:
            rec.status = status
            if status == RecommendationStatus.COMPLETED:
                rec.completed_at = datetime.utcnow()
        return rec
    
    async def get_recommendations_by_finding(self, finding_id: uuid.UUID) -> list:
        return [r for r in self._recommendations.values() if r.finding_id == finding_id]

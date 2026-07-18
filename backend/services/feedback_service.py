"""
Feedback Collection Service
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    ACCURACY = "accuracy"
    USEFULNESS = "usefulness"
    RELEVANCE = "relevance"
    PERFORMANCE = "performance"
    UX = "ux"


@dataclass
class Feedback:
    id: str
    user_id: str
    user_role: str
    feedback_type: FeedbackType
    rating: int  # 1-5
    comment: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_role": self.user_role,
            "feedback_type": self.feedback_type.value,
            "rating": self.rating,
            "comment": self.comment,
            "context": self.context,
            "created_at": self.created_at.isoformat()
        }


class FeedbackService:
    """Feedback collection and analysis service"""

    def __init__(self):
        self.feedbacks: List[Feedback] = []

    def collect_feedback(self, data: Dict[str, Any]) -> Feedback:
        feedback = Feedback(
            id=f"fb_{len(self.feedbacks) + 1}",
            user_id=data.get("user_id", "anonymous"),
            user_role=data.get("user_role", "viewer"),
            feedback_type=FeedbackType(data.get("feedback_type", "accuracy")),
            rating=data.get("rating", 0),
            comment=data.get("comment"),
            context=data.get("context", {})
        )
        self.feedbacks.append(feedback)
        logger.info(f"Feedback collected: {feedback.feedback_type.value} - {feedback.rating}/5")

        # Auto-analyze and trigger improvements if needed
        if feedback.rating <= 2:
            self._trigger_improvement(feedback)

        return feedback

    def _trigger_improvement(self, feedback: Feedback) -> None:
        """Trigger improvement process for low ratings"""
        logger.warning(f"Low rating detected: {feedback.feedback_type.value} - {feedback.rating}/5")

        if feedback.feedback_type == FeedbackType.ACCURACY:
            self._trigger_model_retraining(feedback)

        elif feedback.feedback_type == FeedbackType.PERFORMANCE:
            self._trigger_performance_optimization(feedback)

        elif feedback.feedback_type == FeedbackType.UX:
            self._trigger_ux_improvement(feedback)

    def _trigger_model_retraining(self, feedback: Feedback) -> None:
        """Trigger model retraining"""
        logger.info("⚠️ Model retraining triggered")
        # Implementation: schedule retraining job

    def _trigger_performance_optimization(self, feedback: Feedback) -> None:
        """Trigger performance optimization"""
        logger.info("⚠️ Performance optimization triggered")
        # Implementation: analyze performance metrics

    def _trigger_ux_improvement(self, feedback: Feedback) -> None:
        """Trigger UX improvement"""
        logger.info("⚠️ UX improvement triggered")
        # Implementation: create UX improvement ticket

    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics"""
        total = len(self.feedbacks)
        if total == 0:
            return {"total": 0, "avg_rating": 0}

        by_type = {}
        ratings = []

        for feedback in self.feedbacks:
            key = feedback.feedback_type.value
            by_type[key] = by_type.get(key, {"count": 0, "sum": 0})
            by_type[key]["count"] += 1
            by_type[key]["sum"] += feedback.rating
            ratings.append(feedback.rating)

        avg_overall = sum(ratings) / len(ratings)

        return {
            "total": total,
            "avg_overall": avg_overall,
            "by_type": {
                k: {
                    "count": v["count"],
                    "avg": v["sum"] / v["count"]
                }
                for k, v in by_type.items()
            }
        }


feedback_service = FeedbackService()
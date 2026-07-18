"""
Feedback Loop
Siklus feedback untuk perbaikan model
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeedbackType(str, Enum):
    """Tipe feedback"""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    USEFULNESS = "usefulness"
    SATISFACTION = "satisfaction"
    RECOMMENDATION = "recommendation"


@dataclass
class Feedback:
    """Feedback record"""
    id: str
    source: str  # user, system, model
    type: FeedbackType
    rating: float  # 1-5
    comment: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "type": self.type.value,
            "rating": self.rating,
            "comment": self.comment,
            "context": self.context,
            "created_at": self.created_at.isoformat()
        }


class FeedbackLoop:
    """
    Feedback Loop
    Mengumpulkan dan memproses feedback untuk improvement
    """

    def __init__(self):
        self.feedbacks: List[Feedback] = []
        self.aggregates: Dict[str, Dict[str, float]] = {}

    def collect_feedback(
        self,
        source: str,
        feedback_type: FeedbackType,
        rating: float,
        comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Feedback:
        """
        Collect feedback
        """
        feedback = Feedback(
            id=f"fb_{len(self.feedbacks) + 1}",
            source=source,
            type=feedback_type,
            rating=rating,
            comment=comment,
            context=context or {}
        )

        self.feedbacks.append(feedback)

        # Update aggregates
        key = f"{source}_{feedback_type.value}"
        if key not in self.aggregates:
            self.aggregates[key] = {"sum": 0, "count": 0, "avg": 0}
        self.aggregates[key]["sum"] += rating
        self.aggregates[key]["count"] += 1
        self.aggregates[key]["avg"] = self.aggregates[key]["sum"] / self.aggregates[key]["count"]

        logger.info(f"Feedback collected: {source} - {feedback_type.value} - {rating}")
        return feedback

    def get_feedbacks(
        self,
        source: Optional[str] = None,
        feedback_type: Optional[FeedbackType] = None
    ) -> List[Feedback]:
        """Get feedbacks with filters"""
        results = self.feedbacks

        if source:
            results = [f for f in results if f.source == source]
        if feedback_type:
            results = [f for f in results if f.type == feedback_type]

        return results

    def get_avg_rating(self, source: str, feedback_type: FeedbackType) -> float:
        """Get average rating"""
        key = f"{source}_{feedback_type.value}"
        if key in self.aggregates:
            return self.aggregates[key]["avg"]
        return 0

    def get_model_improvement_metrics(self) -> Dict[str, Any]:
        """
        Get model improvement metrics
        """
        # Get user feedback
        user_feedback = self.get_feedbacks(source="user")

        if not user_feedback:
            return {
                "has_feedback": False,
                "message": "No user feedback collected yet"
            }

        # Calculate metrics
        avg_accuracy = self.get_avg_rating("user", FeedbackType.ACCURACY)
        avg_relevance = self.get_avg_rating("user", FeedbackType.RELEVANCE)
        avg_usefulness = self.get_avg_rating("user", FeedbackType.USEFULNESS)
        avg_satisfaction = self.get_avg_rating("user", FeedbackType.SATISFACTION)

        return {
            "has_feedback": True,
            "feedback_count": len(user_feedback),
            "avg_accuracy": avg_accuracy,
            "avg_relevance": avg_relevance,
            "avg_usefulness": avg_usefulness,
            "avg_satisfaction": avg_satisfaction,
            "overall_score": (avg_accuracy + avg_relevance + avg_usefulness + avg_satisfaction) / 4,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        avg_accuracy = self.get_avg_rating("user", FeedbackType.ACCURACY)
        if avg_accuracy < 3.0:
            recommendations.append("Improve model accuracy - consider retraining with more data")

        avg_relevance = self.get_avg_rating("user", FeedbackType.RELEVANCE)
        if avg_relevance < 3.0:
            recommendations.append("Improve relevance - refine feature selection")

        avg_usefulness = self.get_avg_rating("user", FeedbackType.USEFULNESS)
        if avg_usefulness < 3.0:
            recommendations.append("Improve usefulness - focus on actionable insights")

        return recommendations

    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get feedback summary
        """
        total = len(self.feedbacks)
        by_source = {}
        by_type = {}

        for feedback in self.feedbacks:
            by_source[feedback.source] = by_source.get(feedback.source, 0) + 1
            by_type[feedback.type.value] = by_type.get(feedback.type.value, 0) + 1

        return {
            "total_feedback": total,
            "by_source": by_source,
            "by_type": by_type,
            "avg_rating": sum(f.rating for f in self.feedbacks) / total if total > 0 else 0,
            "recent": [f.to_dict() for f in self.feedbacks[-10:]]
        }


# Singleton instance
feedback_loop = FeedbackLoop()
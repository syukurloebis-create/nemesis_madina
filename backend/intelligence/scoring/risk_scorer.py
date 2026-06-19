# backend/intelligence/scoring/risk_scorer.py
# Replace the entire file with timezone-aware version

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import math

def score(event):
    case_id = getattr(event, "aggregate_id", None)


class RiskScorer:
    """
    Calculate risk scores for cases and entities.
    
    Score ranges:
    - 0-20: Low risk
    - 20-40: Medium-low
    - 40-60: Medium
    - 60-80: High
    - 80-100: Critical
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.weights = self.config.get("weights", {
            "anomaly": 0.35,
            "collusion": 0.25,
            "financial": 0.25,
            "temporal": 0.15,
        })
    
    def _get_now_utc(self) -> datetime:
        """Get current UTC time with timezone"""
        return datetime.now(timezone.utc)
    
    def _ensure_timezone(self, dt: Any) -> Optional[datetime]:
        """Ensure datetime has timezone info (convert to UTC if naive)"""
        if dt is None:
            return None
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            except:
                return None
        if dt.tzinfo is None:
            # Assume UTC for naive datetimes
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    
    def calculate_case_risk(
        self,
        case_data: Dict[str, Any],
        anomaly_result: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for a case.
        
        Args:
            case_data: Case metadata (priority, status, etc.)
            anomaly_result: Result from anomaly detection
            events: List of case events
            
        Returns:
            Dict with scores, level, and recommendations
        """
        # Component scores
        anomaly_score = anomaly_result.get("risk_score", 0) / 100
        collusion_score = self._calculate_collusion_score(events)
        financial_score = self._calculate_financial_score(events)
        temporal_score = self._calculate_temporal_score(case_data, events)
        
        # Weighted overall score
        overall = (
            anomaly_score * self.weights["anomaly"] +
            collusion_score * self.weights["collusion"] +
            financial_score * self.weights["financial"] +
            temporal_score * self.weights["temporal"]
        ) * 100
        
        overall = min(max(overall, 0), 100)
        
        # Determine risk level
        if overall >= 80:
            risk_level = "critical"
        elif overall >= 60:
            risk_level = "high"
        elif overall >= 40:
            risk_level = "medium"
        elif overall >= 20:
            risk_level = "low"
        else:
            risk_level = "info"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            overall, anomaly_score, collusion_score, financial_score
        )
        
        # Identify top risk factors
        factors = []
        if anomaly_score > 0.5:
            factors.append({
                "factor": "anomaly_detection",
                "contribution": round(anomaly_score * self.weights["anomaly"] * 100, 2),
                "description": "Unusual patterns detected in case data"
            })
        if collusion_score > 0.5:
            factors.append({
                "factor": "collusion_risk",
                "contribution": round(collusion_score * self.weights["collusion"] * 100, 2),
                "description": "Potential collusion detected in network"
            })
        if financial_score > 0.5:
            factors.append({
                "factor": "financial_risk",
                "contribution": round(financial_score * self.weights["financial"] * 100, 2),
                "description": "High financial impact or irregular transactions"
            })
        
        return {
            "overall_score": round(overall, 2),
            "risk_level": risk_level,
            "component_scores": {
                "anomaly": round(anomaly_score * 100, 2),
                "collusion": round(collusion_score * 100, 2),
                "financial": round(financial_score * 100, 2),
                "temporal": round(temporal_score * 100, 2),
            },
            "factors": factors,
            "recommendations": recommendations,
            "priority_escalation": overall >= 60,
        }
    
    def _calculate_collusion_score(self, events: List[Dict]) -> float:
        """Calculate collusion risk based on event patterns."""
        if not events:
            return 0.0
        
        score = 0.0
        
        # Extract entities from events
        entities = set()
        for event in events:
            data = event.get("data", {})
            
            for field in ["entity_id", "party_id", "counterparty", "related_case"]:
                if field in data and data[field]:
                    entities.add(str(data[field]))
        
        entity_count = len(entities)
        if entity_count > 3:
            score += min(0.5, (entity_count - 3) * 0.1)
        
        # Check for circular patterns
        involved_cases = set()
        for event in events:
            if event.get("event_type") == "case_merged":
                involved_cases.add(event.get("case_id"))
        
        if len(involved_cases) > 1:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_financial_score(self, events: List[Dict]) -> float:
        """Calculate financial risk based on monetary values."""
        if not events:
            return 0.0
        
        total_amount = 0.0
        max_amount = 0.0
        
        for event in events:
            data = event.get("data", {})
            
            for field in ["amount", "total_loss", "kerugian", "value"]:
                if field in data:
                    amount = data[field]
                    try:
                        amount = float(amount)
                        total_amount += amount
                        max_amount = max(max_amount, amount)
                    except (ValueError, TypeError):
                        pass
        
        score = 0.0
        
        if max_amount >= 1_000_000_000:
            score += 0.8
        elif max_amount >= 100_000_000:
            score += 0.6
        elif max_amount >= 10_000_000:
            score += 0.4
        elif max_amount >= 1_000_000:
            score += 0.2
        
        if total_amount > max_amount * 2:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_temporal_score(
        self,
        case_data: Dict,
        events: List[Dict]
    ) -> float:
        """Calculate temporal risk based on case age and velocity."""
        score = 0.0
        now = self._get_now_utc()
        
        # Case age factor
        created_at = case_data.get("created_at")
        created_at = self._ensure_timezone(created_at)
        
        if created_at:
            age_days = (now - created_at).total_seconds() / 86400
            
            if age_days > 90:
                score += 0.5
            elif age_days > 30:
                score += 0.3
            elif age_days > 7:
                score += 0.1
        
        # Event velocity (events per day)
        if events and created_at:
            event_count = len(events)
            age_days = max(1, (now - created_at).total_seconds() / 86400)
            velocity = event_count / age_days
            
            if velocity > 10:
                score += 0.4
            elif velocity > 5:
                score += 0.2
        
        return min(score, 1.0)
    
    def _generate_recommendations(
        self,
        overall: float,
        anomaly_score: float,
        collusion_score: float,
        financial_score: float
    ) -> List[str]:
        """Generate actionable recommendations based on risk scores."""
        recommendations = []
        
        if overall >= 80:
            recommendations.append("🚨 URGENT: Immediate supervisor notification required")
            recommendations.append("📋 Prioritize for senior investigator assignment")
            recommendations.append("🔒 Consider asset freeze or travel restriction")
        
        if overall >= 60:
            recommendations.append("⚠️ High risk case - expedite review process")
            recommendations.append("👥 Assign additional investigative resources")
        
        if anomaly_score > 0.6:
            recommendations.append("🔍 Conduct detailed anomaly investigation")
            recommendations.append("📊 Request data validation from source")
        
        if collusion_score > 0.5:
            recommendations.append("🕸️ Map relationship network for collusion indicators")
            recommendations.append("🔗 Cross-reference with other cases")
        
        if financial_score > 0.6:
            recommendations.append("💰 Initiate financial forensics audit")
            recommendations.append("🏦 Coordinate with PPATK for suspicious transaction reports")
        
        if not recommendations:
            recommendations.append("✅ Routine monitoring continues")
            recommendations.append("📝 Schedule periodic risk reassessment")
        
        return recommendations
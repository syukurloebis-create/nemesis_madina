# backend/risk/scoring.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .framework import (
    RiskGovernanceFramework, RiskAssessmentResult,
    RiskLevel, RiskTargetType, get_risk_framework
)
from .factors import RiskFactorCalculator, get_factor_calculator


class RiskScoringEngine:
    """Engine untuk menghitung skor risiko"""
    
    def __init__(self):
        self.framework = get_risk_framework()
        self.calculator = get_factor_calculator()
        self._assessment_history: List[RiskAssessmentResult] = []
    
    async def assess_target(
        self,
        target_type: RiskTargetType,
        target_id: uuid.UUID,
        data: Dict[str, Any],
        model_version: str = "v1.0"
    ) -> RiskAssessmentResult:
        """Assess risk for a target"""
        
        assessment_id = uuid.uuid4()
        factor_scores = {}
        factor_details = {}
        
        # Calculate score for each factor
        for factor in self.framework.get_all_factors():
            score = self.calculator.calculate_factor_score(factor, data)
            factor_scores[factor.factor_id] = score
            
            factor_details[factor.factor_id] = {
                "name": factor.name,
                "category": factor.category.value,
                "weight": factor.weight,
                "score": score,
                "weighted_score": score * factor.weight,
                "calculation_method": factor.calculation_method
            }
        
        # Calculate total weighted score
        total_score = sum(
            factor_scores[factor.factor_id] * factor.weight
            for factor in self.framework.get_all_factors()
        )
        
        # Round to 1 decimal
        total_score = round(total_score, 1)
        
        # Determine risk level
        risk_level = self.framework.get_risk_level(total_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(factor_scores, factor_details)
        
        # Create result
        result = RiskAssessmentResult(
            assessment_id=assessment_id,
            target_type=target_type,
            target_id=target_id,
            timestamp=datetime.utcnow(),
            total_score=total_score,
            risk_level=risk_level,
            factor_scores=factor_scores,
            factor_details=factor_details,
            recommendations=recommendations,
            model_version=model_version
        )
        
        # Store in history
        self._assessment_history.append(result)
        
        # Trim history if too large
        if len(self._assessment_history) > 10000:
            self._assessment_history = self._assessment_history[-5000:]
        
        return result
    
    def _generate_recommendations(
        self,
        factor_scores: Dict[str, float],
        factor_details: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on factor scores"""
        
        recommendations = []
        
        # Identify high-risk factors
        high_risk_factors = []
        for factor_id, score in factor_scores.items():
            if score >= 70:
                high_risk_factors.append((factor_id, score))
        
        # Sort by score (highest first)
        high_risk_factors.sort(key=lambda x: x[1], reverse=True)
        
        # Add recommendations for top 3 high-risk factors
        for factor_id, score in high_risk_factors[:3]:
            factor_info = factor_details.get(factor_id, {})
            factor_name = factor_info.get("name", factor_id)
            
            if factor_id == "vendor_dominance":
                recommendations.append(
                    f"Review vendor dominance - {factor_name} shows high concentration ({score:.0f}%)"
                )
            elif factor_id == "conflict_of_interest":
                recommendations.append(
                    f"Investigate potential conflict of interest - {factor_name} detected ({score:.0f}%)"
                )
            elif factor_id == "single_bidder":
                recommendations.append(
                    f"Review procurement process - high single bidder rate ({score:.0f}%)"
                )
            elif factor_id == "price_markup":
                recommendations.append(
                    f"Verify price reasonableness - potential markup detected ({score:.0f}%)"
                )
            elif factor_id == "collusion_network":
                recommendations.append(
                    f"Analyze collusion network - entity is centrally connected ({score:.0f}%)"
                )
            elif factor_id == "evidence_quality":
                recommendations.append(
                    f"Strengthen evidence collection - evidence quality is low ({score:.0f}%)"
                )
            else:
                recommendations.append(
                    f"Review {factor_name} - high risk score ({score:.0f}%)"
                )
        
        if not recommendations:
            recommendations.append("No immediate high-risk factors detected")
        
        return recommendations
    
    async def get_last_assessment(
        self,
        target_type: RiskTargetType,
        target_id: uuid.UUID
    ) -> Optional[RiskAssessmentResult]:
        """Get last assessment for target"""
        
        assessments = [
            a for a in self._assessment_history
            if a.target_type == target_type and a.target_id == target_id
        ]
        
        if not assessments:
            return None
        
        # Return most recent
        return max(assessments, key=lambda a: a.timestamp)
    
    async def get_assessment_history(
        self,
        target_type: RiskTargetType,
        target_id: uuid.UUID,
        limit: int = 10
    ) -> List[RiskAssessmentResult]:
        """Get assessment history for target"""
        
        assessments = [
            a for a in self._assessment_history
            if a.target_type == target_type and a.target_id == target_id
        ]
        
        assessments.sort(key=lambda a: a.timestamp, reverse=True)
        return assessments[:limit]
    
    async def get_high_risk_targets(
        self,
        target_type: RiskTargetType,
        min_score: float = 70,
        limit: int = 20
    ) -> List[RiskAssessmentResult]:
        """Get high risk targets"""
        
        assessments = [
            a for a in self._assessment_history
            if a.target_type == target_type and a.total_score >= min_score
        ]
        
        # Get latest assessment per target
        latest_per_target = {}
        for a in assessments:
            key = a.target_id
            if key not in latest_per_target or a.timestamp > latest_per_target[key].timestamp:
                latest_per_target[key] = a
        
        results = list(latest_per_target.values())
        results.sort(key=lambda a: a.total_score, reverse=True)
        
        return results[:limit]
    
    async def get_risk_summary(
        self,
        target_type: Optional[RiskTargetType] = None
    ) -> Dict[str, Any]:
        """Get risk summary statistics"""
        
        assessments = self._assessment_history
        if target_type:
            assessments = [a for a in assessments if a.target_type == target_type]
        
        if not assessments:
            return {
                "total_assessments": 0,
                "average_score": 0,
                "distribution": {},
                "latest_assessments": []
            }
        
        # Calculate average score
        avg_score = sum(a.total_score for a in assessments) / len(assessments)
        
        # Calculate distribution by risk level
        distribution = {
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.CRITICAL.value: 0
        }
        
        for a in assessments:
            distribution[a.risk_level.value] += 1
        
        # Get latest 10 assessments
        latest = sorted(assessments, key=lambda a: a.timestamp, reverse=True)[:10]
        
        return {
            "total_assessments": len(assessments),
            "average_score": round(avg_score, 1),
            "distribution": distribution,
            "latest_assessments": [a.to_dict() for a in latest]
        }


# Singleton instance
_scoring_engine = None

def get_scoring_engine() -> RiskScoringEngine:
    """Get singleton scoring engine"""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = RiskScoringEngine()
    return _scoring_engine
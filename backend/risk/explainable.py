# backend/risk/explainable.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .framework import RiskAssessmentResult, RiskLevel, RiskTargetType
from .scoring import get_scoring_engine


class ExplainableRisk:
    """Explainable risk dengan faktor breakdown"""
    
    def __init__(self, assessment: RiskAssessmentResult):
        self.assessment = assessment
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of risk assessment"""
        return {
            "assessment_id": str(self.assessment.assessment_id),
            "target_type": self.assessment.target_type.value,
            "target_id": str(self.assessment.target_id),
            "total_score": self.assessment.total_score,
            "risk_level": self.assessment.risk_level.value,
            "timestamp": self.assessment.timestamp.isoformat(),
            "model_version": self.assessment.model_version
        }
    
    def get_factor_breakdown(self) -> Dict[str, Any]:
        """Get detailed factor breakdown"""
        
        breakdown = {
            "factors": [],
            "total_weighted_score": 0,
            "high_risk_factors": [],
            "contributing_factors": []
        }
        
        for factor_id, details in self.assessment.factor_details.items():
            weighted_score = details["weighted_score"]
            breakdown["total_weighted_score"] += weighted_score
            
            factor_info = {
                "factor_id": factor_id,
                "name": details["name"],
                "category": details["category"],
                "score": details["score"],
                "weight": details["weight"],
                "weighted_score": weighted_score,
                "contribution_percentage": 0,  # Calculated below
                "status": "HIGH" if details["score"] >= 70 else "MEDIUM" if details["score"] >= 40 else "LOW"
            }
            
            breakdown["factors"].append(factor_info)
            
            if details["score"] >= 70:
                breakdown["high_risk_factors"].append(factor_info)
        
        # Calculate contribution percentages
        total = breakdown["total_weighted_score"]
        for factor in breakdown["factors"]:
            if total > 0:
                factor["contribution_percentage"] = round(factor["weighted_score"] / total * 100, 1)
            else:
                factor["contribution_percentage"] = 0
            
            # Add to contributing factors if significant
            if factor["contribution_percentage"] >= 10:
                breakdown["contributing_factors"].append(factor)
        
        # Sort by contribution
        breakdown["contributing_factors"].sort(key=lambda x: x["contribution_percentage"], reverse=True)
        breakdown["high_risk_factors"].sort(key=lambda x: x["score"], reverse=True)
        
        return breakdown
    
    def get_risk_drivers(self) -> List[Dict[str, Any]]:
        """Get main risk drivers"""
        
        drivers = []
        for factor_id, details in self.assessment.factor_details.items():
            if details["score"] >= 60:  # Significant risk
                drivers.append({
                    "factor": details["name"],
                    "category": details["category"],
                    "score": details["score"],
                    "impact": "High" if details["score"] >= 80 else "Medium",
                    "description": self._get_factor_description(factor_id, details["score"])
                })
        
        # Sort by score
        drivers.sort(key=lambda x: x["score"], reverse=True)
        return drivers
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get actionable recommendations"""
        
        recommendations = []
        
        for rec in self.assessment.recommendations:
            # Categorize recommendations
            if "vendor" in rec.lower() or "dominance" in rec.lower():
                category = "PROCUREMENT"
                priority = "HIGH" if "high" in rec.lower() else "MEDIUM"
            elif "conflict" in rec.lower() or "interest" in rec.lower():
                category = "GOVERNANCE"
                priority = "HIGH"
            elif "evidence" in rec.lower():
                category = "EVIDENCE"
                priority = "MEDIUM"
            elif "collusion" in rec.lower() or "network" in rec.lower():
                category = "INTELLIGENCE"
                priority = "HIGH"
            else:
                category = "GENERAL"
                priority = "MEDIUM"
            
            recommendations.append({
                "text": rec,
                "category": category,
                "priority": priority
            })
        
        return recommendations
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get data for risk visualization"""
        
        breakdown = self.get_factor_breakdown()
        
        # Data for radar chart
        radar_data = {
            "categories": {},
            "factors": []
        }
        
        for factor in breakdown["factors"]:
            category = factor["category"]
            if category not in radar_data["categories"]:
                radar_data["categories"][category] = []
            radar_data["categories"][category].append(factor["score"])
            radar_data["factors"].append({
                "name": factor["name"],
                "score": factor["score"],
                "category": category
            })
        
        # Calculate category averages
        category_averages = {}
        for category, scores in radar_data["categories"].items():
            category_averages[category] = round(sum(scores) / len(scores), 1)
        
        return {
            "radar_data": radar_data["factors"],
            "category_averages": category_averages,
            "total_score": self.assessment.total_score,
            "risk_level": self.assessment.risk_level.value,
            "drivers": self.get_risk_drivers()[:5]
        }
    
    def _get_factor_description(self, factor_id: str, score: float) -> str:
        """Get description for risk factor"""
        
        descriptions = {
            "vendor_dominance": f"Vendor dominates {score:.0f}% of procurement market",
            "conflict_of_interest": "Potential conflict of interest detected",
            "single_bidder": f"High single bidder rate: {score:.0f}%",
            "price_markup": f"Price markup detected: {score:.0f}% above benchmark",
            "collusion_network": f"Central position in collusion network (score: {score:.0f}%)",
            "evidence_quality": f"Evidence quality below threshold: {score:.0f}%",
            "timeline_integrity": f"Timeline gaps detected: {score:.0f}% integrity"
        }
        
        return descriptions.get(factor_id, f"Risk factor score: {score:.0f}%")
    
    def to_dict(self) -> Dict[str, Any]:
        """Complete explainable risk report"""
        return {
            "summary": self.get_summary(),
            "factor_breakdown": self.get_factor_breakdown(),
            "risk_drivers": self.get_risk_drivers(),
            "recommendations": self.get_recommendations(),
            "visualization": self.get_visualization_data()
        }


class ExplainableRiskService:
    """Service untuk explainable risk"""
    
    def __init__(self):
        self.scoring_engine = get_scoring_engine()
    
    async def get_risk_report(
        self,
        target_type: RiskTargetType,
        target_id: uuid.UUID
    ) -> Optional[Dict[str, Any]]:
        """Get explainable risk report for target"""
        
        assessment = await self.scoring_engine.get_last_assessment(target_type, target_id)
        
        if not assessment:
            return None
        
        explainable = ExplainableRisk(assessment)
        return explainable.to_dict()
    
    async def compare_risks(
        self,
        target_type: RiskTargetType,
        target_ids: List[uuid.UUID]
    ) -> Dict[str, Any]:
        """Compare risks across multiple targets"""
        
        assessments = []
        for target_id in target_ids:
            assessment = await self.scoring_engine.get_last_assessment(target_type, target_id)
            if assessment:
                assessments.append(assessment)
        
        if not assessments:
            return {"comparisons": [], "summary": {}}
        
        # Prepare comparison data
        comparisons = []
        for a in assessments:
            explainable = ExplainableRisk(a)
            comparisons.append({
                "target_id": str(a.target_id),
                "score": a.total_score,
                "level": a.risk_level.value,
                "top_drivers": explainable.get_risk_drivers()[:3]
            })
        
        # Sort by score
        comparisons.sort(key=lambda x: x["score"], reverse=True)
        
        # Summary
        scores = [c["score"] for c in comparisons]
        summary = {
            "highest_score": max(scores),
            "lowest_score": min(scores),
            "average_score": round(sum(scores) / len(scores), 1),
            "total_targets": len(comparisons),
            "risk_distribution": {
                RiskLevel.CRITICAL.value: len([c for c in comparisons if c["level"] == RiskLevel.CRITICAL.value]),
                RiskLevel.HIGH.value: len([c for c in comparisons if c["level"] == RiskLevel.HIGH.value]),
                RiskLevel.MEDIUM.value: len([c for c in comparisons if c["level"] == RiskLevel.MEDIUM.value]),
                RiskLevel.LOW.value: len([c for c in comparisons if c["level"] == RiskLevel.LOW.value])
            }
        }
        
        return {"comparisons": comparisons, "summary": summary}


# Singleton instance
_explainable_risk_service = None

def get_explainable_risk_service() -> ExplainableRiskService:
    """Get singleton explainable risk service"""
    global _explainable_risk_service
    if _explainable_risk_service is None:
        _explainable_risk_service = ExplainableRiskService()
    return _explainable_risk_service
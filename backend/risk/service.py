# backend/risk/service.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .framework import RiskTargetType, RiskLevel, get_risk_framework
from .scoring import get_scoring_engine
from .explainable import get_explainable_risk_service, ExplainableRiskService


class RiskGovernanceService:
    """Integrated risk governance service"""
    
    def __init__(self):
        self.framework = get_risk_framework()
        self.scoring_engine = get_scoring_engine()
        self.explainable_service = get_explainable_risk_service()
    
    async def assess_case_risk(
        self,
        case_id: uuid.UUID,
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for a case"""
        
        result = await self.scoring_engine.assess_target(
            target_type=RiskTargetType.CASE,
            target_id=case_id,
            data=case_data
        )
        
        return result.to_dict()
    
    async def assess_entity_risk(
        self,
        entity_id: uuid.UUID,
        entity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for an entity"""
        
        result = await self.scoring_engine.assess_target(
            target_type=RiskTargetType.ENTITY,
            target_id=entity_id,
            data=entity_data
        )
        
        return result.to_dict()
    
    async def assess_vendor_risk(
        self,
        vendor_id: uuid.UUID,
        vendor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk for a vendor"""
        
        result = await self.scoring_engine.assess_target(
            target_type=RiskTargetType.VENDOR,
            target_id=vendor_id,
            data=vendor_data
        )
        
        return result.to_dict()
    
    async def get_risk_report(
        self,
        target_type: RiskTargetType,
        target_id: uuid.UUID
    ) -> Optional[Dict[str, Any]]:
        """Get complete risk report"""
        
        return await self.explainable_service.get_risk_report(target_type, target_id)
    
    async def get_high_risk_entities(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get high risk entities"""
        
        results = await self.scoring_engine.get_high_risk_targets(
            target_type=RiskTargetType.ENTITY,
            min_score=70,
            limit=limit
        )
        
        return [r.to_dict() for r in results]
    
    async def get_high_risk_cases(
        self,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get high risk cases"""
        
        results = await self.scoring_engine.get_high_risk_targets(
            target_type=RiskTargetType.CASE,
            min_score=70,
            limit=limit
        )
        
        return [r.to_dict() for r in results]
    
    async def get_risk_dashboard(
        self
    ) -> Dict[str, Any]:
        """Get risk dashboard data"""
        
        # Get summaries for different target types
        case_summary = await self.scoring_engine.get_risk_summary(RiskTargetType.CASE)
        entity_summary = await self.scoring_engine.get_risk_summary(RiskTargetType.ENTITY)
        
        # Get top high risk items
        top_cases = await self.get_high_risk_cases(limit=10)
        top_entities = await self.get_high_risk_entities(limit=10)
        
        # Get framework info
        framework_info = self.framework.to_dict()
        
        return {
            "summary": {
                "cases": case_summary,
                "entities": entity_summary
            },
            "top_risks": {
                "cases": top_cases,
                "entities": top_entities
            },
            "framework": framework_info,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_risk_level_from_score(self, score: float) -> str:
        """Get risk level from score"""
        return self.framework.get_risk_level(score).value
    
    def get_thresholds(self) -> Dict[str, Dict[str, int]]:
        """Get risk thresholds"""
        thresholds = {}
        for level in RiskLevel:
            min_val, max_val = self.framework.get_threshold(level)
            thresholds[level.value] = {"min": min_val, "max": max_val}
        return thresholds


# Singleton instance
_risk_governance_service = None

def get_risk_governance_service() -> RiskGovernanceService:
    """Get singleton risk governance service"""
    global _risk_governance_service
    if _risk_governance_service is None:
        _risk_governance_service = RiskGovernanceService()
    return _risk_governance_service
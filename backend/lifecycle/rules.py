# backend/lifecycle/rules.py
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class TransitionRules:
    """Rules for validating transition conditions"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    async def check_case_complete(self, case_id: uuid.UUID) -> bool:
        """Check if case has all required fields"""
        # Implementasi: query case dari database
        # Periksa apakah title, description, priority ada
        return True  # Placeholder
    
    async def check_screening_complete(self, case_id: uuid.UUID) -> bool:
        """Check if screening is complete"""
        # Implementasi: cek apakah screening_result sudah diisi
        return True  # Placeholder
    
    async def check_evidence_minimum(self, case_id: uuid.UUID) -> bool:
        """Check if case has minimum evidence"""
        # Implementasi: count evidence untuk case ini, minimal 1
        return True  # Placeholder
    
    async def check_screening_rejected(self, case_id: uuid.UUID) -> bool:
        """Check if screening result is rejected"""
        # Implementasi: cek screening_result == "REJECTED"
        return False  # Placeholder
    
    async def check_risk_assessed(self, case_id: uuid.UUID) -> bool:
        """Check if risk assessment has been performed"""
        # Implementasi: cek apakah risk_score sudah diisi
        return True  # Placeholder
    
    async def check_priority_assigned(self, case_id: uuid.UUID) -> bool:
        """Check if priority has been assigned"""
        # Implementasi: cek apakah priority sudah diisi
        return True  # Placeholder
    
    async def check_low_risk(self, case_id: uuid.UUID) -> bool:
        """Check if risk is low"""
        # Implementasi: cek risk_score < 30
        return False  # Placeholder
    
    async def check_no_fraud_indication(self, case_id: uuid.UUID) -> bool:
        """Check if no fraud indication found"""
        # Implementasi: cek tidak ada temuan fraud
        return False  # Placeholder
    
    async def check_evidence_sufficient(self, case_id: uuid.UUID) -> bool:
        """Check if evidence is sufficient for findings"""
        # Implementasi: cek jumlah evidence > 3
        return True  # Placeholder
    
    async def check_analysis_complete(self, case_id: uuid.UUID) -> bool:
        """Check if forensic analysis is complete"""
        # Implementasi: cek status analysis
        return True  # Placeholder
    
    async def check_finding_approved(self, case_id: uuid.UUID) -> bool:
        """Check if findings have been approved"""
        # Implementasi: cek approval status findings
        return True  # Placeholder
    
    async def check_recommendation_issued(self, case_id: uuid.UUID) -> bool:
        """Check if recommendations have been issued"""
        # Implementasi: cek apakah recommendation sudah dibuat
        return True  # Placeholder
    
    async def check_followup_complete(self, case_id: uuid.UUID) -> bool:
        """Check if follow-up actions are complete"""
        # Implementasi: cek status follow-up
        return True  # Placeholder
    
    async def check_recovery_recorded(self, case_id: uuid.UUID) -> bool:
        """Check if recovery has been recorded"""
        # Implementasi: cek apakah recovery_action sudah dicatat
        return True  # Placeholder
    
    async def check_stale_case(self, case_id: uuid.UUID) -> bool:
        """Check if case is stale"""
        # Implementasi: cek last activity > 90 days
        return False  # Placeholder
    
    async def check_no_activity_days(self, case_id: uuid.UUID, days: int) -> bool:
        """Check if case has no activity for specified days"""
        # Implementasi: cek last activity > days
        return False  # Placeholder


class RuleEngine:
    """Engine for evaluating transition rules"""
    
    def __init__(self, rules: TransitionRules):
        self.rules = rules
        self._condition_map = {
            "case_complete": rules.check_case_complete,
            "screening_complete": rules.check_screening_complete,
            "evidence_minimum": rules.check_evidence_minimum,
            "screening_rejected": rules.check_screening_rejected,
            "risk_assessed": rules.check_risk_assessed,
            "priority_assigned": rules.check_priority_assigned,
            "low_risk": rules.check_low_risk,
            "no_fraud_indication": rules.check_no_fraud_indication,
            "evidence_sufficient": rules.check_evidence_sufficient,
            "analysis_complete": rules.check_analysis_complete,
            "finding_approved": rules.check_finding_approved,
            "recommendation_issued": rules.check_recommendation_issued,
            "followup_complete": rules.check_followup_complete,
            "recovery_recorded": rules.check_recovery_recorded,
            "stale_case": rules.check_stale_case,
        }
    
    async def evaluate_condition(self, condition_name: str, case_id: uuid.UUID) -> bool:
        """Evaluate a single condition"""
        handler = self._condition_map.get(condition_name)
        if handler:
            return await handler(case_id)
        return False
    
    async def evaluate_conditions(self, condition_names: List[str], case_id: uuid.UUID) -> Dict[str, bool]:
        """Evaluate multiple conditions"""
        results = {}
        for condition in condition_names:
            results[condition] = await self.evaluate_condition(condition, case_id)
        return results
    
    async def all_conditions_met(self, condition_names: List[str], case_id: uuid.UUID) -> bool:
        """Check if all conditions are met"""
        results = await self.evaluate_conditions(condition_names, case_id)
        return all(results.values())